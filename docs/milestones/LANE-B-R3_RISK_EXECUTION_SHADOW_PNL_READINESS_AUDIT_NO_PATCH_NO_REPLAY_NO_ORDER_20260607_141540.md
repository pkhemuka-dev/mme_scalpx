# LANE-B-R3_RISK_EXECUTION_SHADOW_PNL_READINESS_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141540
2026-06-07T14:15:40+05:30

LAW=READINESS_AUDIT_ONLY_NO_PATCH_NO_REPLAY_NO_ORDER_NO_REDIS_DELETE_NO_LIVE_NO_PAPER_NO_RISK_NO_EXECUTION

## R2F2 freeze proof
R2F2=run/proofs/LANE-B-R2F2_CORRECTED_REPLAY_WORKSTATION_SMOKE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141428.json
{
  "tag": "LANE-B-R2F2_CORRECTED_REPLAY_WORKSTATION_SMOKE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141428",
  "classification": "PASS_R2F2_REPLAY_WORKSTATION_SMOKE_FREEZE_WITH_FINGERPRINT_CAVEAT",
  "patch_applied": false,
  "replay_executed": false,
  "broker_order": false,
  "paper_live": false,
  "redis_delete": false,
  "risk_execution_start": false,
  "pnl_grade": false,
  "next_batch": "LANE-B-R3_RISK_EXECUTION_SHADOW_PNL_READINESS_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER",
  "report": "run/audits/LANE-B-R2F2_CORRECTED_REPLAY_WORKSTATION_SMOKE_FREEZE_NO_PATCH_NO_REPLAY_NO_ORDER_20260607_141428_report.md"
}

## Replay PnL/risk/execution-shadow source surfaces
FOUND bin/replay_run.py
FOUND app/mme_scalpx/replay/risk_adapter.py
FOUND app/mme_scalpx/replay/execution_shadow.py
FOUND app/mme_scalpx/replay/fill_model.py
FOUND app/mme_scalpx/replay/metrics.py
FOUND app/mme_scalpx/replay/artifacts.py
FOUND app/mme_scalpx/replay/reports.py
FOUND app/mme_scalpx/replay/report_exporter.py
FOUND app/mme_scalpx/replay/contracts.py

## CLI scope/fill-model evidence
                     [--session-segment SESSION_SEGMENT] --doctrine-mode
                     {locked,shadow,differential} --scope
                     {feeds_only,feeds_features,feeds_features_strategy,feeds_features_strategy_risk,feeds_features_strategy_risk_execution_shadow,full_system_replay}
                     [--dataset-id DATASET_ID] [--fill-model FILL_MODEL]
                     [--run-root RUN_ROOT]
  --doctrine-mode {locked,shadow,differential}
  --scope {feeds_only,feeds_features,feeds_features_strategy,feeds_features_strategy_risk,feeds_features_strategy_risk_execution_shadow,full_system_replay}
                        Replay topology scope
  --fill-model FILL_MODEL
  --run-root RUN_ROOT
HELP_RC=0

## Import smoke for risk/execution-shadow/PnL modules
IMPORT_PASS app.mme_scalpx.replay.risk_adapter
IMPORT_PASS app.mme_scalpx.replay.execution_shadow
IMPORT_PASS app.mme_scalpx.replay.fill_model
IMPORT_PASS app.mme_scalpx.replay.metrics
IMPORT_PASS app.mme_scalpx.replay.artifacts
IMPORT_PASS app.mme_scalpx.replay.report_exporter
IMPORT_PASS app.mme_scalpx.replay.contracts
IMPORT_RC=0

## Static symbol scan for PnL/fill/trade fields
app/mme_scalpx/replay/risk_adapter.py:10:REPLAY_RISK_ADAPTER_CONTRACT_VERSION = "replay_risk_adapter_v1"
app/mme_scalpx/replay/risk_adapter.py:15:    "risk_evaluated",
app/mme_scalpx/replay/risk_adapter.py:16:    "research_trade_allowed",
app/mme_scalpx/replay/risk_adapter.py:17:    "entry_vetoed",
app/mme_scalpx/replay/risk_adapter.py:19:    "risk_score",
app/mme_scalpx/replay/risk_adapter.py:20:    "max_loss_points",
app/mme_scalpx/replay/risk_adapter.py:33:    risk_evaluated: bool
app/mme_scalpx/replay/risk_adapter.py:34:    research_trade_allowed: bool
app/mme_scalpx/replay/risk_adapter.py:35:    entry_vetoed: bool
app/mme_scalpx/replay/risk_adapter.py:37:    risk_score: float
app/mme_scalpx/replay/risk_adapter.py:38:    max_loss_points: float
app/mme_scalpx/replay/risk_adapter.py:48:def build_replay_risk_decision(
app/mme_scalpx/replay/risk_adapter.py:52:    max_loss_points: float = 12.0,
app/mme_scalpx/replay/risk_adapter.py:72:    risk_score = float(winner.get("score", 0.0)) if isinstance(winner, Mapping) else 0.0
app/mme_scalpx/replay/risk_adapter.py:73:    entry_vetoed = bool(veto_reasons)
app/mme_scalpx/replay/risk_adapter.py:78:        risk_evaluated=True,
app/mme_scalpx/replay/risk_adapter.py:79:        research_trade_allowed=bool(winner) and not entry_vetoed,
app/mme_scalpx/replay/risk_adapter.py:80:        entry_vetoed=entry_vetoed,
app/mme_scalpx/replay/risk_adapter.py:82:        risk_score=risk_score,
app/mme_scalpx/replay/risk_adapter.py:83:        max_loss_points=float(max_loss_points),
app/mme_scalpx/replay/risk_adapter.py:89:        "risk_evaluated": decision.risk_evaluated,
app/mme_scalpx/replay/risk_adapter.py:90:        "research_trade_allowed": decision.research_trade_allowed,
app/mme_scalpx/replay/risk_adapter.py:91:        "entry_vetoed": decision.entry_vetoed,
app/mme_scalpx/replay/risk_adapter.py:93:        "risk_score": decision.risk_score,
app/mme_scalpx/replay/risk_adapter.py:94:        "max_loss_points": decision.max_loss_points,
app/mme_scalpx/replay/risk_adapter.py:102:        "risk_parity": "NOT_PROVEN_IN_27I",
app/mme_scalpx/replay/risk_adapter.py:103:        "risk_shape_parity": "PROVEN_BY_27I",
app/mme_scalpx/replay/risk_adapter.py:107:def validate_replay_risk_decision(decision: Mapping[str, Any]) -> dict[str, Any]:
app/mme_scalpx/replay/risk_adapter.py:117:    ok = bool(not missing and decision.get("risk_evaluated") is True and no_order_ok)
app/mme_scalpx/replay/risk_adapter.py:122:        "risk_evaluated": decision.get("risk_evaluated") is True,
app/mme_scalpx/replay/risk_adapter.py:126:def publish_replay_risk_shadow(
app/mme_scalpx/replay/risk_adapter.py:130:    risk_decision: Mapping[str, Any],
app/mme_scalpx/replay/risk_adapter.py:133:    validation = validate_replay_risk_decision(risk_decision)
app/mme_scalpx/replay/risk_adapter.py:135:        raise ValueError(f"invalid replay risk decision: {validation}")
app/mme_scalpx/replay/risk_adapter.py:138:        surface="risk_shadow",
app/mme_scalpx/replay/risk_adapter.py:139:        row=dict(risk_decision),
app/mme_scalpx/replay/risk_adapter.py:144:def replay_risk_adapter_contract_summary() -> dict[str, Any]:
app/mme_scalpx/replay/risk_adapter.py:148:        "risk_shape_parity": "PROVEN_BY_27I",
app/mme_scalpx/replay/risk_adapter.py:149:        "real_risk_parity": "NOT_PROVEN_IN_27I",
app/mme_scalpx/replay/risk_adapter.py:167:    "build_replay_risk_decision",
app/mme_scalpx/replay/risk_adapter.py:168:    "validate_replay_risk_decision",
app/mme_scalpx/replay/risk_adapter.py:169:    "publish_replay_risk_shadow",
app/mme_scalpx/replay/risk_adapter.py:170:    "replay_risk_adapter_contract_summary",
app/mme_scalpx/replay/execution_shadow.py:10:REPLAY_EXECUTION_SHADOW_CONTRACT_VERSION = "replay_execution_shadow_v1"
app/mme_scalpx/replay/execution_shadow.py:23:    "fill_policy",
app/mme_scalpx/replay/execution_shadow.py:24:    "fill_status",
app/mme_scalpx/replay/execution_shadow.py:26:    "filled_qty",
app/mme_scalpx/replay/execution_shadow.py:27:    "entry_price",
app/mme_scalpx/replay/execution_shadow.py:28:    "exit_price",
app/mme_scalpx/replay/execution_shadow.py:31:    "shadow_trade_log",
app/mme_scalpx/replay/execution_shadow.py:32:    "shadow_pnl_summary",
app/mme_scalpx/replay/execution_shadow.py:43:    fill_policy: str = "FULL_FILL"
app/mme_scalpx/replay/execution_shadow.py:45:    partial_fill_ratio: float = 0.5
app/mme_scalpx/replay/execution_shadow.py:46:    entry_reference_price: float = 100.0
app/mme_scalpx/replay/execution_shadow.py:47:    exit_reference_price: float = 104.0
app/mme_scalpx/replay/execution_shadow.py:59:    if profile.fill_policy not in REPLAY_SHADOW_FILL_POLICIES:
app/mme_scalpx/replay/execution_shadow.py:60:        raise ValueError(f"unsupported replay shadow fill_policy: {profile.fill_policy}")
app/mme_scalpx/replay/execution_shadow.py:62:        "fill_policy": profile.fill_policy,
app/mme_scalpx/replay/execution_shadow.py:64:        "partial_fill_ratio": float(profile.partial_fill_ratio),
app/mme_scalpx/replay/execution_shadow.py:65:        "entry_reference_price": float(profile.entry_reference_price),
app/mme_scalpx/replay/execution_shadow.py:66:        "exit_reference_price": float(profile.exit_reference_price),
app/mme_scalpx/replay/execution_shadow.py:77:def simulate_replay_execution_shadow(
app/mme_scalpx/replay/execution_shadow.py:81:    risk_decision: Mapping[str, Any],
app/mme_scalpx/replay/execution_shadow.py:84:    fill_policy = str(assumption_profile.get("fill_policy", "FULL_FILL"))
app/mme_scalpx/replay/execution_shadow.py:85:    if fill_policy not in REPLAY_SHADOW_FILL_POLICIES:
app/mme_scalpx/replay/execution_shadow.py:86:        raise ValueError(f"unsupported replay shadow fill_policy: {fill_policy}")
app/mme_scalpx/replay/execution_shadow.py:89:    partial_ratio = max(0.0, min(1.0, float(assumption_profile.get("partial_fill_ratio", 0.5))))
app/mme_scalpx/replay/execution_shadow.py:90:    entry_ref = float(assumption_profile.get("entry_reference_price", 100.0))
app/mme_scalpx/replay/execution_shadow.py:91:    exit_ref = float(assumption_profile.get("exit_reference_price", entry_ref))
app/mme_scalpx/replay/execution_shadow.py:95:    research_allowed = risk_decision.get("research_trade_allowed") is True
app/mme_scalpx/replay/execution_shadow.py:96:    risk_vetoed = risk_decision.get("entry_vetoed") is True
app/mme_scalpx/replay/execution_shadow.py:98:    if risk_vetoed or not research_allowed:
app/mme_scalpx/replay/execution_shadow.py:99:        fill_status = "RISK_VETOED"
app/mme_scalpx/replay/execution_shadow.py:100:        filled_qty = 0
app/mme_scalpx/replay/execution_shadow.py:101:    elif fill_policy == "FULL_FILL":
app/mme_scalpx/replay/execution_shadow.py:102:        fill_status = "FILLED"
app/mme_scalpx/replay/execution_shadow.py:103:        filled_qty = requested_qty
app/mme_scalpx/replay/execution_shadow.py:104:    elif fill_policy == "PARTIAL_FILL":
app/mme_scalpx/replay/execution_shadow.py:105:        fill_status = "PARTIAL_FILLED"
app/mme_scalpx/replay/execution_shadow.py:106:        filled_qty = _clamp_qty(requested_qty * partial_ratio)
app/mme_scalpx/replay/execution_shadow.py:107:    elif fill_policy == "NO_FILL":
app/mme_scalpx/replay/execution_shadow.py:108:        fill_status = "NO_FILL"
app/mme_scalpx/replay/execution_shadow.py:109:        filled_qty = 0
app/mme_scalpx/replay/execution_shadow.py:111:        fill_status = "REJECTED"
app/mme_scalpx/replay/execution_shadow.py:112:        filled_qty = 0
app/mme_scalpx/replay/execution_shadow.py:114:    entry_price = entry_ref + slippage if filled_qty else None
app/mme_scalpx/replay/execution_shadow.py:115:    exit_price = exit_ref - slippage if filled_qty else None
app/mme_scalpx/replay/execution_shadow.py:116:    gross_points = (exit_price - entry_price) if filled_qty and entry_price is not None and exit_price is not None else 0.0
app/mme_scalpx/replay/execution_shadow.py:117:    net_points = gross_points - costs if filled_qty else 0.0
app/mme_scalpx/replay/execution_shadow.py:118:    net_pnl = net_points * filled_qty
app/mme_scalpx/replay/execution_shadow.py:120:    winning_family = None
app/mme_scalpx/replay/execution_shadow.py:124:        winning_family = arbitration.get("winning_family")
app/mme_scalpx/replay/execution_shadow.py:127:    shadow_trade = {
app/mme_scalpx/replay/execution_shadow.py:128:        "schema_version": "replay_shadow_trade_v1",
app/mme_scalpx/replay/execution_shadow.py:130:        "winning_family": winning_family,
app/mme_scalpx/replay/execution_shadow.py:132:        "fill_policy": fill_policy,
app/mme_scalpx/replay/execution_shadow.py:133:        "fill_status": fill_status,
app/mme_scalpx/replay/execution_shadow.py:135:        "filled_qty": filled_qty,
app/mme_scalpx/replay/execution_shadow.py:136:        "entry_price": entry_price,
app/mme_scalpx/replay/execution_shadow.py:137:        "exit_price": exit_price,
app/mme_scalpx/replay/execution_shadow.py:141:        "net_pnl": net_pnl,
app/mme_scalpx/replay/execution_shadow.py:149:        "position_opened": filled_qty > 0,
app/mme_scalpx/replay/execution_shadow.py:150:        "position_closed": filled_qty > 0,
app/mme_scalpx/replay/execution_shadow.py:152:        "filled_qty": filled_qty,
app/mme_scalpx/replay/execution_shadow.py:154:        "family": winning_family,
app/mme_scalpx/replay/execution_shadow.py:158:    pnl_summary = {
app/mme_scalpx/replay/execution_shadow.py:159:        "schema_version": "replay_shadow_pnl_summary_v1",
app/mme_scalpx/replay/execution_shadow.py:161:        "trade_count": 1 if filled_qty else 0,
app/mme_scalpx/replay/execution_shadow.py:162:        "filled_qty": filled_qty,
app/mme_scalpx/replay/execution_shadow.py:165:        "net_pnl": net_pnl,
app/mme_scalpx/replay/execution_shadow.py:166:        "is_profit": net_pnl > 0,
app/mme_scalpx/replay/execution_shadow.py:167:        "is_loss": net_pnl < 0,
app/mme_scalpx/replay/execution_shadow.py:174:        "fill_policy": fill_policy,
app/mme_scalpx/replay/execution_shadow.py:175:        "fill_status": fill_status,
app/mme_scalpx/replay/execution_shadow.py:177:        "filled_qty": filled_qty,
app/mme_scalpx/replay/execution_shadow.py:178:        "entry_price": entry_price,
app/mme_scalpx/replay/execution_shadow.py:179:        "exit_price": exit_price,
app/mme_scalpx/replay/execution_shadow.py:182:        "shadow_trade_log": (shadow_trade,),
app/mme_scalpx/replay/execution_shadow.py:183:        "shadow_pnl_summary": pnl_summary,
app/mme_scalpx/replay/execution_shadow.py:184:        "risk_vetoed": risk_vetoed,
app/mme_scalpx/replay/execution_shadow.py:185:        "research_trade_allowed": research_allowed,
app/mme_scalpx/replay/execution_shadow.py:193:        "execution_shadow_shape": "PROVEN_BY_27I",
app/mme_scalpx/replay/execution_shadow.py:199:def validate_replay_execution_shadow(payload: Mapping[str, Any]) -> dict[str, Any]:
app/mme_scalpx/replay/execution_shadow.py:201:    fill_policy_ok = payload.get("fill_policy") in REPLAY_SHADOW_FILL_POLICIES
app/mme_scalpx/replay/execution_shadow.py:211:    pnl_ok = isinstance(payload.get("shadow_pnl_summary"), Mapping)
app/mme_scalpx/replay/execution_shadow.py:212:    trade_log_ok = isinstance(payload.get("shadow_trade_log"), tuple)
app/mme_scalpx/replay/execution_shadow.py:214:    ok = bool(not missing and fill_policy_ok and no_real_order_ok and pnl_ok and trade_log_ok and position_ok)
app/mme_scalpx/replay/execution_shadow.py:218:        "fill_policy_ok": fill_policy_ok,
app/mme_scalpx/replay/execution_shadow.py:220:        "pnl_ok": pnl_ok,
app/mme_scalpx/replay/execution_shadow.py:221:        "trade_log_ok": trade_log_ok,
app/mme_scalpx/replay/execution_shadow.py:226:def publish_replay_execution_shadow(
app/mme_scalpx/replay/execution_shadow.py:230:    execution_shadow: Mapping[str, Any],
app/mme_scalpx/replay/execution_shadow.py:233:    validation = validate_replay_execution_shadow(execution_shadow)
app/mme_scalpx/replay/execution_shadow.py:238:        surface="execution_shadow",
app/mme_scalpx/replay/execution_shadow.py:239:        row=dict(execution_shadow),
app/mme_scalpx/replay/execution_shadow.py:244:def replay_execution_shadow_contract_summary() -> dict[str, Any]:
app/mme_scalpx/replay/execution_shadow.py:247:        "fill_policies": REPLAY_SHADOW_FILL_POLICIES,
app/mme_scalpx/replay/execution_shadow.py:249:        "execution_shadow_shape": "PROVEN_BY_27I",
app/mme_scalpx/replay/execution_shadow.py:250:        "pnl_shadow_math": "PROVEN_BY_27I",
app/mme_scalpx/replay/execution_shadow.py:272:    "simulate_replay_execution_shadow",
app/mme_scalpx/replay/execution_shadow.py:273:    "validate_replay_execution_shadow",
app/mme_scalpx/replay/execution_shadow.py:274:    "publish_replay_execution_shadow",
app/mme_scalpx/replay/execution_shadow.py:275:    "replay_execution_shadow_contract_summary",
app/mme_scalpx/replay/fill_model.py:2:app/mme_scalpx/replay/fill_model.py
app/mme_scalpx/replay/fill_model.py:4:Freeze-grade replay-only fill model layer for the MME-ScalpX Permanent Replay &
app/mme_scalpx/replay/fill_model.py:10:- canonical replay-only fill request/result contracts
app/mme_scalpx/replay/fill_model.py:11:- deterministic fill model taxonomy
app/mme_scalpx/replay/fill_model.py:12:- replay-only fill decision logic
app/mme_scalpx/replay/fill_model.py:25:- fill behavior here is replay-only and must never be treated as broker truth
app/mme_scalpx/replay/fill_model.py:26:- all fill assumptions must be explicit and auditable
app/mme_scalpx/replay/fill_model.py:40:    """Base exception for replay fill-model failures."""
app/mme_scalpx/replay/fill_model.py:44:    """Raised when fill-model inputs are invalid."""
app/mme_scalpx/replay/fill_model.py:50:    Canonical replay-only fill request.
app/mme_scalpx/replay/fill_model.py:70:    Canonical replay-only fill result.
app/mme_scalpx/replay/fill_model.py:75:    filled: bool
app/mme_scalpx/replay/fill_model.py:76:    fill_qty: int
app/mme_scalpx/replay/fill_model.py:77:    fill_price: float | None
app/mme_scalpx/replay/fill_model.py:86:    Canonical fill model config.
app/mme_scalpx/replay/fill_model.py:91:    allow_partial_fills: bool = False
app/mme_scalpx/replay/fill_model.py:96:    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
app/mme_scalpx/replay/fill_model.py:103:    - BUY fills at best_ask if present, else market_price
app/mme_scalpx/replay/fill_model.py:104:    - SELL fills at best_bid if present, else market_price
app/mme_scalpx/replay/fill_model.py:105:    - full fill only
app/mme_scalpx/replay/fill_model.py:116:    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
app/mme_scalpx/replay/fill_model.py:119:        fill_price = _resolve_immediate_market_fill_price(request)
app/mme_scalpx/replay/fill_model.py:120:        if fill_price is None:
app/mme_scalpx/replay/fill_model.py:124:                filled=False,
app/mme_scalpx/replay/fill_model.py:125:                fill_qty=0,
app/mme_scalpx/replay/fill_model.py:126:                fill_price=None,
app/mme_scalpx/replay/fill_model.py:128:                reason="no_fill_price_available",
app/mme_scalpx/replay/fill_model.py:135:            slippage = fill_price - reference
app/mme_scalpx/replay/fill_model.py:140:            filled=True,
app/mme_scalpx/replay/fill_model.py:141:            fill_qty=request.qty,
app/mme_scalpx/replay/fill_model.py:142:            fill_price=fill_price,
app/mme_scalpx/replay/fill_model.py:144:            reason="immediate_market_fill",
app/mme_scalpx/replay/fill_model.py:152:    - BUY fills if market/ask <= order_price
app/mme_scalpx/replay/fill_model.py:153:    - SELL fills if market/bid >= order_price
app/mme_scalpx/replay/fill_model.py:154:    - full fill only
app/mme_scalpx/replay/fill_model.py:165:    def fill(self, request: ReplayFillRequest) -> ReplayFillResult:
app/mme_scalpx/replay/fill_model.py:169:                "limit-touch fill model requires order_price"
app/mme_scalpx/replay/fill_model.py:172:        fill_price = _resolve_limit_touch_fill_price(request)
app/mme_scalpx/replay/fill_model.py:173:        if fill_price is None:
app/mme_scalpx/replay/fill_model.py:177:                filled=False,
app/mme_scalpx/replay/fill_model.py:178:                fill_qty=0,
app/mme_scalpx/replay/fill_model.py:179:                fill_price=None,
app/mme_scalpx/replay/fill_model.py:188:            slippage = fill_price - reference
app/mme_scalpx/replay/fill_model.py:193:            filled=True,
app/mme_scalpx/replay/fill_model.py:194:            fill_qty=request.qty,
app/mme_scalpx/replay/fill_model.py:195:            fill_price=fill_price,
app/mme_scalpx/replay/fill_model.py:197:            reason="limit_touch_fill",
app/mme_scalpx/replay/fill_model.py:204:    Freeze-grade replay fill model factory.
app/mme_scalpx/replay/fill_model.py:223:            f"unsupported fill model name: {config.model_name!r}"
app/mme_scalpx/replay/fill_model.py:227:def fill_request_to_dict(request: ReplayFillRequest) -> dict[str, Any]:
app/mme_scalpx/replay/fill_model.py:242:def fill_result_to_dict(result: ReplayFillResult) -> dict[str, Any]:
app/mme_scalpx/replay/fill_model.py:246:        "filled": result.filled,
app/mme_scalpx/replay/fill_model.py:247:        "fill_qty": result.fill_qty,
app/mme_scalpx/replay/fill_model.py:248:        "fill_price": result.fill_price,
app/mme_scalpx/replay/fill_model.py:260:    if config.allow_partial_fills:
app/mme_scalpx/replay/fill_model.py:262:            "partial fills are not yet supported in frozen fill model"
app/mme_scalpx/replay/fill_model.py:294:def _resolve_immediate_market_fill_price(request: ReplayFillRequest) -> float | None:
app/mme_scalpx/replay/fill_model.py:304:def _resolve_limit_touch_fill_price(request: ReplayFillRequest) -> float | None:
app/mme_scalpx/replay/fill_model.py:329:    "fill_request_to_dict",
app/mme_scalpx/replay/fill_model.py:330:    "fill_result_to_dict",
app/mme_scalpx/replay/fill_model.py:335:def replay_fill_model_shadow_assumption_profiles():
app/mme_scalpx/replay/fill_model.py:336:    """Return replay-only fill policies supported by execution_shadow."""
app/mme_scalpx/replay/fill_model.py:337:    from app.mme_scalpx.replay.execution_shadow import REPLAY_SHADOW_FILL_POLICIES
app/mme_scalpx/replay/fill_model.py:340:        "schema_version": "replay_fill_model_shadow_assumption_profiles_v1",
app/mme_scalpx/replay/fill_model.py:341:        "fill_policies": tuple(REPLAY_SHADOW_FILL_POLICIES),
app/mme_scalpx/replay/fill_model.py:355:    "replay_fill_model_shadow_assumption_profiles",
app/mme_scalpx/replay/artifacts.py:39:# RAW-S producer family emission hook — replay-only, non-live.
app/mme_scalpx/replay/artifacts.py:41:    from app.mme_scalpx.replay.raw_producer_family_emission import emit_family_context as _raw_s_emit_family_context
app/mme_scalpx/replay/artifacts.py:43:    def _raw_s_emit_family_context(value, *, source_artifact=""):
app/mme_scalpx/replay/artifacts.py:59:    return _raw_s_emit_family_context(value, source_artifact=source_artifact)
app/mme_scalpx/replay/artifacts.py:60:# END RAW-S producer family emission hook.
app/mme_scalpx/replay/artifacts.py:277:    def write_trade_log_csv(
app/mme_scalpx/replay/artifacts.py:285:            artifact_plan.trade_log_path,
app/mme_scalpx/replay/artifacts.py:310:    def write_exit_breakdown(
app/mme_scalpx/replay/artifacts.py:315:        return self.write_json_artifact(artifact_plan.exit_breakdown_path, payload)
app/mme_scalpx/replay/artifacts.py:403:            "1", "true", "yes", "y", "ok", "pass", "candidate", "entry", "buy", "sell"
app/mme_scalpx/replay/artifacts.py:537:        replay decisions, broker/order behavior, paper/live behavior, risk,
app/mme_scalpx/replay/artifacts.py:551:            "target_points": ["TARGET_POINTS", "target_points", "profit_target"],
app/mme_scalpx/replay/artifacts.py:605:            "app/mme_scalpx/services/strategy_family/",
app/mme_scalpx/replay/artifacts.py:637:            if "strategy_family" in path_text:
app/mme_scalpx/replay/artifacts.py:670:                "prefer explicit non-zero strategy_family constants/config doctrine authority",
app/mme_scalpx/replay/artifacts.py:686:            candidate = self._b3_r32_first_present(flat, ["candidate", "candidate_fallback", "candidate_found", "candidate_ok", "entry_candidate"])
app/mme_scalpx/replay/artifacts.py:702:            enriched_values["entry_mode"] = "NO_ENTRY_HOLD_ONLY"
app/mme_scalpx/replay/artifacts.py:703:            enrichment_sources["entry_mode"] = {
app/mme_scalpx/replay/artifacts.py:706:                "not_trade_entry_proof": True,
app/mme_scalpx/replay/artifacts.py:786:                "Values are source-labelled and must not be treated as trade/PnL proof.",
app/mme_scalpx/replay/artifacts.py:787:                "entry_mode=NO_ENTRY_HOLD_ONLY is only an export label when all rows are HOLD and candidate_true_count is zero.",
app/mme_scalpx/replay/artifacts.py:788:                "Do not claim paper/live, broker/order, risk/execution, or profitability readiness from this enrichment.",
app/mme_scalpx/replay/artifacts.py:800:            "entry_mode",
app/mme_scalpx/replay/artifacts.py:850:            "note": "This is economics field completeness only; it is not PnL or trade profitability.",
app/mme_scalpx/replay/artifacts.py:857:    def _b3_r32_write_family_side_summary_export(self, artifact_plan, strategy_rows):
app/mme_scalpx/replay/artifacts.py:862:            "family",
app/mme_scalpx/replay/artifacts.py:874:            family = self._b3_r32_first_present(flat, ["family", "strategy_family", "strategy_family_id", "strategy_id", "strategy", "strategy_name"])
app/mme_scalpx/replay/artifacts.py:880:            family_text = self._b3_r32_str(family, "UNKNOWN")
app/mme_scalpx/replay/artifacts.py:885:            decode_quality = "weak" if family_text == "UNKNOWN" else "ok"
app/mme_scalpx/replay/artifacts.py:887:            counts[(family_text, side_text, linked_text, metadata_text, leg_text, decode_quality)] += 1
app/mme_scalpx/replay/artifacts.py:891:                "family": key[0],
app/mme_scalpx/replay/artifacts.py:902:        path = Path(getattr(artifact_plan, "artifacts_dir", getattr(artifact_plan, "root_dir", "."))) / "family_side_summary.csv"
app/mme_scalpx/replay/artifacts.py:913:        broker/order paths, or touch paper/live/risk/execution.
app/mme_scalpx/replay/artifacts.py:1057:        combined_family_side_rows = []
app/mme_scalpx/replay/artifacts.py:1074:            family_side_path = _find_named_file(run_dir, artifacts_dir, "family_side_summary.csv")
app/mme_scalpx/replay/artifacts.py:1080:            family_side_rows = _read_csv(family_side_path)
app/mme_scalpx/replay/artifacts.py:1091:            for row in family_side_rows:
app/mme_scalpx/replay/artifacts.py:1093:                combined_family_side_rows.append(enriched)
app/mme_scalpx/replay/artifacts.py:1121:                "family_side_rows": len(family_side_rows),
app/mme_scalpx/replay/artifacts.py:1143:            "combined_family_side_rows": len(combined_family_side_rows),
app/mme_scalpx/replay/artifacts.py:1147:                "No Redis, broker/order, paper/live, risk/execution side effects.",
app/mme_scalpx/replay/artifacts.py:1167:                ["source_date", "source_run_dir", "artifacts_dir", "integrity_verdict", "candidate_rows", "blocker_rows", "family_side_rows", "economics_summary_present"],
app/mme_scalpx/replay/artifacts.py:1179:            "combined_family_side_summary": _write_csv(
app/mme_scalpx/replay/artifacts.py:1180:                out_dir / "combined_family_side_summary.csv",
app/mme_scalpx/replay/artifacts.py:1181:                combined_family_side_rows,
app/mme_scalpx/replay/artifacts.py:1182:                ["source_date", "source_run_dir", "family", "side", "linked_feature_side", "metadata_side", "selected_leg", "decode_quality", "count"],
app/mme_scalpx/replay/artifacts.py:1195:            "combined_family_side_rows": len(combined_family_side_rows),
app/mme_scalpx/replay/artifacts.py:1204:        broker/order behavior, paper/live behavior, risk, or execution.
app/mme_scalpx/replay/artifacts.py:1225:            family_side_rows = self._b3_r32_write_family_side_summary_export(artifact_plan, strategy_rows)
app/mme_scalpx/replay/artifacts.py:1237:                "family_side_summary_rows": len(family_side_rows),
app/mme_scalpx/replay/artifacts.py:1426:        "trade_log_path",

## Existing replay risk/execution-shadow proofs, if any
docs/milestones/2026-04-25_replay_integrity_execution_shadow_persist_20260425_153204.md
docs/milestones/2026-04-25_replay_integrity_execution_shadow_writepoint_20260425_152919.md
docs/milestones/B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133.md
docs/milestones/B1-PROFIT-HANDOFF-R0_AFTER_MARKET_STATUS_AND_NEXT_DAY_PLAN_NO_ORDER_consolidate_profitability_pnl_candidate_dhan_status_and_next_day_live_plan_no_patch_no_start_no_order_20260520_234701.md
docs/milestones/B1-PROFIT-SIM-R1_RECORDED_CANDIDATE_PNL_PRECHECK_NO_ORDER_after_market_precheck_candidate_pnl_files_from_recorded_inventory_no_start_no_order_20260520_232330.md
docs/milestones/B1-PROFIT-SIM-R2_RECORDED_PNL_SUMMARY_NO_ORDER_after_market_summarize_recorded_pnl_csvs_from_r1_precheck_no_start_no_order_20260520_232551.md
docs/milestones/B1-PROFIT-SIM-R3_PNL_EVIDENCE_DEEP_INSPECTION_NO_ORDER_inspect_recorded_pnl_csv_columns_lot_size_trade_count_duplicate_status_no_start_no_order_20260520_233335.md
docs/milestones/B1-R26_EXECUTION_SHADOW_SEAM_AUDIT_NO_PATCH_NO_START_locate_execution_shadow_no_broker_seam_20260517_161940_milestone.md
docs/milestones/B1-R27_EXECUTION_SHADOW_BOOTSTRAP_ROUTE_PLAN_NO_PATCH_NO_START_map_existing_execution_shadow_bootstrap_route_20260517_162107_milestone.md
docs/milestones/B1-R29_MAIN_HELPER_SHADOW_ROUTE_BINDING_PATCH_DRY_PROOF_NO_START_bind_observe_only_execution_shadow_no_broker_route_20260517_162549_milestone.md
docs/milestones/B1A-R30_RETRY_HELPER_EXECUTE_AFTER_SHADOW_ROUTE_PATCH_APPROVAL_REQUIRED_guarded_helper_execute_after_shadow_route_patch_verify_streams_no_replay_no_pnl_no_order_20260517_164308.md
docs/milestones/B1A-R32_APPLY_HELPER_SERVICE_SELECTION_AND_MAIN_EXECUTION_SHADOW_BINDING_PATCH_NO_START_patch_helper_per_service_selection_and_main_execution_shadow_no_broker_binding_no_start_20260517_165051.md
docs/milestones/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008.md
docs/milestones/B1A-R38_LIFECYCLE_TRIGGER_PATCH_APPROVAL_REQUIRED_patch_observe_only_lifecycle_publishers_for_risk_execution_no_start_no_replay_no_pnl_20260517_171410.md
docs/milestones/B1A-R41_STATUS_ONLY_LIFECYCLE_ATTESTATION_FOR_B1B_NO_PATCH_NO_START_machine_readable_attestation_lifecycle_rows_status_only_for_b1b_r4d_no_replay_no_pnl_20260517_173407.md
docs/milestones/B1B-R4D_ACCEPT_B1A_STATUS_ONLY_ATTESTATION_RUNTIME_LIFECYCLE_ACCEPTED_NO_BACKTEST_NO_PNL_ingest_b1a_r41_attestation_accept_runtime_lifecycle_keep_backtest_not_admitted_pnl_not_ready_20260517_173549.md
docs/milestones/B1B-R5_BACKTEST_ADMISSION_REMAINS_NOT_ADMITTED_PENDING_VALID_TRADE_LIFECYCLE_freeze_runtime_lifecycle_accepted_but_backtest_pnl_blocked_until_valid_trade_lifecycle_no_patch_no_start_20260517_173722.md
docs/milestones/B3-R10_FIX_FEATURE_DECISION_DATASET_LAYOUT_NO_ORDER_stage_opt_ticks_required_and_features_decisions_optional_then_test_valid_replay_scopes_no_broker_order_pnl_20260521_125540.md
docs/milestones/B3-R11_ONE_STRATEGY_DETERMINISTIC_DRY_REPLAY_NO_ORDER_run_two_deterministic_feeds_features_strategy_dry_replays_for_mist_call_no_broker_order_pnl_20260521_133642.md
docs/milestones/B3-R1_LIVE_DATASET_ADMISSION_AUDIT_NO_START_NO_REPLAY_NO_ORDER_audit_existing_live_streams_for_replay_dataset_admission_without_start_stop_replay_order_pnl_20260521_101008.md
docs/milestones/B3-R25A_REPLAY_ROW_SURFACE_DEEP_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_strategy_decisions_features_rows_risk_execution_shadow_for_candidate_blocker_economics_fields_20260528_231726.md
docs/milestones/B3-R3_OFFLINE_REPLAY_DRY_RUN_FROM_CAPTURED_SURFACES_ZERODHA_ONLY_NO_BROKER_NO_ORDER_run_or_block_offline_replay_mvp_dry_run_from_b3_r2_manifest_without_broker_order_pnl_20260521_102211.md
docs/milestones/B3-R4_DETERMINISTIC_OFFLINE_REPLAY_EXECUTION_DRY_ONLY_NO_BROKER_NO_ORDER_run_deterministic_offline_replay_cli_dry_only_from_mvp_dataset_no_broker_order_pnl_20260521_102417.md
docs/milestones/B3-R9_ONE_STRATEGY_DRY_REPLAY_COMPATIBILITY_CHECK_NO_ORDER_check_replay_cli_strategy_stage_compatibility_using_b3_r8_mist_call_adapter_no_broker_order_pnl_20260521_125333.md
docs/milestones/LANE-F-R0_VALID_TRADE_LIFECYCLE_EVIDENCE_INVENTORY_NO_PATCH_NO_START_read_only_inventory_for_valid_trade_lifecycle_data_after_b1b_r5_wait_state_no_replay_no_pnl_20260517_173947.md
docs/milestones/LANE-F-R1_VALIDATE_CANDIDATE_LIFECYCLE_FILES_NO_REPLAY_NO_PNL_read_only_validate_possible_lifecycle_candidate_files_from_lane_f_r0_no_admission_no_replay_no_pnl_20260517_174249.md
docs/milestones/LANE-F-R2_CAPTURE_PLAN_FOR_FUTURE_VALID_TRADE_LIFECYCLE_DATA_NO_START_freeze_future_live_session_valid_trade_lifecycle_capture_plan_no_patch_no_start_no_replay_no_pnl_20260517_174422.md
docs/milestones/LANE-F-R4R10_RUNTIME_GATE_PATCH_PLAN_NO_PATCH_NO_START_after_market_deep_patch_plan_for_family_runtime_disabled_gate_no_patch_no_start_no_replay_no_pnl_20260518_150607.md
docs/milestones/LANE-F-R4R12_DIAGNOSTIC_PATCH_STATIC_PROOF_NO_START_static_verify_r4r11r_diagnostic_helpers_compile_zero_order_no_start_no_replay_no_pnl_20260518_152329.md
docs/milestones/LANE-F-R4R13R2_TINY_LIVE_DECISION_DIAGNOSTIC_CAPTURE_NO_ORDER_tiny_recovery_capture_current_decision_diagnostic_fields_no_start_no_replay_no_pnl_20260519_102918.md
docs/milestones/LANE-F-R4R14_DIAGNOSTIC_WIRING_PATCH_PLAN_NO_PATCH_NO_START_plan_wiring_runtime_gate_diagnostics_into_decision_output_no_patch_no_start_no_replay_no_pnl_20260519_103156.md
docs/milestones/LANE-F-R4R15B_NO_SIGNAL_CONSTRUCTION_PATH_REVIEW_NO_PATCH_NO_START_find_actual_no_signal_runtime_disabled_item_construction_before_wiring_patch_no_start_no_replay_no_pnl_20260519_103619.md
docs/milestones/LANE-F-R4R15C_EXACT_FUNCTION_WIRING_PATCH_PLAN_RECOVERY_NO_PATCH_NO_START_recover_exact_function_plan_after_broken_paste_no_patch_no_start_no_replay_no_pnl_20260519_105219.md
docs/milestones/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_105909.md
docs/milestones/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_110548.md
docs/milestones/LANE-F-R4R15G_MERGE_DIAGNOSTICS_INTO_RAW_PATCH_PLAN_NO_PATCH_NO_START_plan_exact_raw_merge_diagnostic_wiring_patch_no_patch_no_start_no_replay_no_pnl_20260519_110917.md
docs/milestones/LANE-F-R4R15H_RAW_MERGE_DIAGNOSTIC_WIRING_PATCH_APPROVAL_REQUIRED_patch_activation_raw_merge_runtime_diagnostics_no_start_no_replay_no_pnl_no_order_20260519_224247.md
docs/milestones/LANE-F-R4R15_DIAGNOSTIC_WIRING_PATCH_APPROVAL_REQUIRED_patch_runtime_gate_diagnostics_into_strategy_decision_output_only_no_start_no_replay_no_pnl_no_order_20260519_103327.md
docs/milestones/LANE-F-R4R16_RAW_MERGE_WIRING_STATIC_PROOF_NO_START_static_verify_r4r15h_raw_merge_patch_compile_zero_order_no_start_no_replay_no_pnl_20260519_224330.md
docs/milestones/LANE-F-R4R17A_OBSERVE_ONLY_STRATEGY_RESTART_DECISION_REQUIRED_NO_ORDER_decide_next_live_session_observe_only_restart_needed_for_raw_diagnostic_visibility_no_start_no_replay_no_pnl_20260519_225039.md
docs/milestones/LANE-F-R4R17R_TAIL_DECISION_DIAGNOSTIC_VISIBILITY_CAPTURE_NO_ORDER_recover_r4r17_with_tail_based_decision_capture_no_xread_no_start_no_replay_no_pnl_20260519_224820.md
docs/milestones/LANE-F-R4R18AR_RECOVER_AFTERMARKET_HANDOFF_BUNDLE_NO_START_recover_archive_packaging_after_relative_path_error_no_start_no_replay_no_pnl_20260519_231123.md
docs/milestones/LANE-F-R4R18A_AFTERMARKET_RAW_DIAGNOSTIC_PATCH_HANDOFF_BUNDLE_NO_START_compact_bundle_raw_diagnostic_patch_evidence_next_live_session_no_start_no_replay_no_pnl_20260519_230750.md
docs/milestones/LANE-F-R4R18B_ORPHAN_MAIN_PROCESS_CLASSIFICATION_NO_START_classify_generic_main_process_after_r4r18_preflight_no_start_no_order_no_replay_no_pnl_20260520_093120.md
docs/milestones/LANE-F-R4R18_OBSERVE_ONLY_STACK_RESTART_PREFLIGHT_NO_START_live_session_preflight_before_observe_only_feeds_features_strategy_restart_no_order_no_replay_no_pnl_20260520_092948.md
docs/milestones/LANE-F-R4R19H5_APPROVED_INSTRUMENT_METADATA_REFRESH_NO_ORDER_NO_REPLAY_approved_refresh_nfo_instrument_metadata_after_feeds_stale_failure_no_order_no_replay_no_pnl_20260520_100348.md
docs/milestones/LANE-F-R4R4_DECISION_TAIL_AUDIT_AFTER_NO_LIFECYCLE_NO_PATCH_NO_START_read_only_audit_latest_decisions_after_live_capture_no_candidate_no_replay_no_pnl_20260518_143451.md
docs/milestones/LANE-F-R4R5_STRATEGY_BLOCKER_AUDIT_NO_PATCH_NO_START_read_only_audit_strategy_blockers_after_no_candidate_decisions_no_replay_no_pnl_20260518_143812.md
docs/milestones/LANE-F-R4R6_DATA_QUALITY_BLOCKER_AUDIT_NO_PATCH_NO_START_read_only_audit_stage_data_quality_ok_failed_from_live_features_decisions_no_replay_no_pnl_20260518_144017.md
docs/milestones/LANE-F-R4R7_RUNTIME_ENABLEMENT_SURFACE_AUDIT_NO_PATCH_NO_START_read_only_audit_why_classic_and_miso_runtime_disabled_no_order_no_replay_no_pnl_20260518_144147.md
docs/milestones/LANE-F-R4R8R2_RUNTIME_GATE_MINIMAL_PATCH_PLAN_NO_PATCH_NO_START_minimal_recovery_plan_after_broken_paste_no_live_change_no_replay_no_pnl_20260518_144956.md
docs/milestones/LANE-F-R4R9R_SOURCE_REVIEW_RECOVERY_NO_PATCH_NO_START_compact_runtime_gate_source_review_after_broken_paste_no_replay_no_pnl_20260518_145356.md
docs/milestones/batch_raw_aa14_pnl_cost_model_source_resolver_20260502_112226.md
docs/milestones/batch_raw_aa14_pnl_cost_model_source_resolver_20260502_112815.md
docs/milestones/batch_raw_aa17_r2_trade_lifecycle_pnl_authority_resolver_20260502_125729.md
docs/milestones/batch_raw_aa3_canonical_trade_pnl_ranking_20260501_180316.md
docs/milestones/batch_raw_e_pnl_analytics_freeze_final_20260501_130154.md
docs/milestones/batch_raw_r_family_pnl_gap_review_freeze_final_20260501_143807.md
docs/milestones/replay_data_a14_execution_shadow_20260508T184414Z.md
docs/milestones/replay_data_a14_execution_shadow_20260508T184835Z.md
docs/milestones/replay_data_a18_execution_shadow_semantic_normalization_20260508T191103Z.md
docs/milestones/replay_data_a65_artifact_audit_execution_shadow_precheck_20260510T141909Z.md
docs/milestones/replay_data_a65_r2_integrity_stem_equivalence_execution_shadow_precheck_20260510T142256Z.md
docs/milestones/replay_data_a66_execution_shadow_durable_start_20260510T142418Z.md
docs/milestones/replay_data_a67_post_execution_shadow_audit_next_scope_precheck_20260510T142850Z.md
docs/runbooks/B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133_dedicated_dhan_context_service_design.md
docs/runbooks/B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133_next_route_runbook.md
docs/runbooks/B1-PROFIT-HANDOFF-R0_AFTER_MARKET_STATUS_AND_NEXT_DAY_PLAN_NO_ORDER_consolidate_profitability_pnl_candidate_dhan_status_and_next_day_live_plan_no_patch_no_start_no_order_20260520_234701_next_day_plan.md
docs/runbooks/B1-PROFIT-SIM-R1_RECORDED_CANDIDATE_PNL_PRECHECK_NO_ORDER_after_market_precheck_candidate_pnl_files_from_recorded_inventory_no_start_no_order_20260520_232330_next_route_runbook.md
docs/runbooks/B1-PROFIT-SIM-R2_RECORDED_PNL_SUMMARY_NO_ORDER_after_market_summarize_recorded_pnl_csvs_from_r1_precheck_no_start_no_order_20260520_232551_next_route_runbook.md
docs/runbooks/B1-PROFIT-SIM-R3_PNL_EVIDENCE_DEEP_INSPECTION_NO_ORDER_inspect_recorded_pnl_csv_columns_lot_size_trade_count_duplicate_status_no_start_no_order_20260520_233335_next_route_runbook.md
docs/runbooks/B1-R26_EXECUTION_SHADOW_SEAM_AUDIT_NO_PATCH_NO_START_locate_execution_shadow_no_broker_seam_20260517_161940_runbook.md
docs/runbooks/B1-R27_EXECUTION_SHADOW_BOOTSTRAP_ROUTE_PLAN_NO_PATCH_NO_START_map_existing_execution_shadow_bootstrap_route_20260517_162107_runbook.md
docs/runbooks/B1-R29_MAIN_HELPER_SHADOW_ROUTE_BINDING_PATCH_DRY_PROOF_NO_START_bind_observe_only_execution_shadow_no_broker_route_20260517_162549_runbook.md
docs/runbooks/B1A-R30_RETRY_HELPER_EXECUTE_AFTER_SHADOW_ROUTE_PATCH_APPROVAL_REQUIRED_guarded_helper_execute_after_shadow_route_patch_verify_streams_no_replay_no_pnl_no_order_20260517_164308_next_route_runbook.md
docs/runbooks/B1A-R32_APPLY_HELPER_SERVICE_SELECTION_AND_MAIN_EXECUTION_SHADOW_BINDING_PATCH_NO_START_patch_helper_per_service_selection_and_main_execution_shadow_no_broker_binding_no_start_20260517_165051_next_execute_runbook.md
docs/runbooks/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_next_execute_runbook.md
docs/runbooks/B1A-R38_LIFECYCLE_TRIGGER_PATCH_APPROVAL_REQUIRED_patch_observe_only_lifecycle_publishers_for_risk_execution_no_start_no_replay_no_pnl_20260517_171410_next_execute_runbook.md
docs/runbooks/B1A-R41_STATUS_ONLY_LIFECYCLE_ATTESTATION_FOR_B1B_NO_PATCH_NO_START_machine_readable_attestation_lifecycle_rows_status_only_for_b1b_r4d_no_replay_no_pnl_20260517_173407_b1b_r4d_next_route_runbook.md
docs/runbooks/B1B-R4D_ACCEPT_B1A_STATUS_ONLY_ATTESTATION_RUNTIME_LIFECYCLE_ACCEPTED_NO_BACKTEST_NO_PNL_ingest_b1a_r41_attestation_accept_runtime_lifecycle_keep_backtest_not_admitted_pnl_not_ready_20260517_173549_next_route_runbook.md
docs/runbooks/B1B-R5_BACKTEST_ADMISSION_REMAINS_NOT_ADMITTED_PENDING_VALID_TRADE_LIFECYCLE_freeze_runtime_lifecycle_accepted_but_backtest_pnl_blocked_until_valid_trade_lifecycle_no_patch_no_start_20260517_173722_next_route_runbook.md
docs/runbooks/B3-R10_FIX_FEATURE_DECISION_DATASET_LAYOUT_NO_ORDER_stage_opt_ticks_required_and_features_decisions_optional_then_test_valid_replay_scopes_no_broker_order_pnl_20260521_125540_next_route_runbook.md
docs/runbooks/B3-R11_ONE_STRATEGY_DETERMINISTIC_DRY_REPLAY_NO_ORDER_run_two_deterministic_feeds_features_strategy_dry_replays_for_mist_call_no_broker_order_pnl_20260521_133642_next_route_runbook.md
docs/runbooks/B3-R1_LIVE_DATASET_ADMISSION_AUDIT_NO_START_NO_REPLAY_NO_ORDER_audit_existing_live_streams_for_replay_dataset_admission_without_start_stop_replay_order_pnl_20260521_101008_next_route_runbook.md
docs/runbooks/B3-R25A_REPLAY_ROW_SURFACE_DEEP_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_strategy_decisions_features_rows_risk_execution_shadow_for_candidate_blocker_economics_fields_20260528_231726_next_route_runbook.md
docs/runbooks/B3-R3_OFFLINE_REPLAY_DRY_RUN_FROM_CAPTURED_SURFACES_ZERODHA_ONLY_NO_BROKER_NO_ORDER_run_or_block_offline_replay_mvp_dry_run_from_b3_r2_manifest_without_broker_order_pnl_20260521_102211_next_route_runbook.md
docs/runbooks/B3-R4_DETERMINISTIC_OFFLINE_REPLAY_EXECUTION_DRY_ONLY_NO_BROKER_NO_ORDER_run_deterministic_offline_replay_cli_dry_only_from_mvp_dataset_no_broker_order_pnl_20260521_102417_next_route_runbook.md
docs/runbooks/B3-R9_ONE_STRATEGY_DRY_REPLAY_COMPATIBILITY_CHECK_NO_ORDER_check_replay_cli_strategy_stage_compatibility_using_b3_r8_mist_call_adapter_no_broker_order_pnl_20260521_125333_next_route_runbook.md
docs/runbooks/LANE-F-R0_VALID_TRADE_LIFECYCLE_EVIDENCE_INVENTORY_NO_PATCH_NO_START_read_only_inventory_for_valid_trade_lifecycle_data_after_b1b_r5_wait_state_no_replay_no_pnl_20260517_173947_next_route_runbook.md
docs/runbooks/LANE-F-R1_VALIDATE_CANDIDATE_LIFECYCLE_FILES_NO_REPLAY_NO_PNL_read_only_validate_possible_lifecycle_candidate_files_from_lane_f_r0_no_admission_no_replay_no_pnl_20260517_174249_next_route_runbook.md
docs/runbooks/LANE-F-R2_CAPTURE_PLAN_FOR_FUTURE_VALID_TRADE_LIFECYCLE_DATA_NO_START_freeze_future_live_session_valid_trade_lifecycle_capture_plan_no_patch_no_start_no_replay_no_pnl_20260517_174422_future_live_session_runbook.md
docs/runbooks/LANE-F-R4R10_RUNTIME_GATE_PATCH_PLAN_NO_PATCH_NO_START_after_market_deep_patch_plan_for_family_runtime_disabled_gate_no_patch_no_start_no_replay_no_pnl_20260518_150607_next_route_runbook.md
docs/runbooks/LANE-F-R4R12_DIAGNOSTIC_PATCH_STATIC_PROOF_NO_START_static_verify_r4r11r_diagnostic_helpers_compile_zero_order_no_start_no_replay_no_pnl_20260518_152329_next_route_runbook.md
docs/runbooks/LANE-F-R4R13R2_TINY_LIVE_DECISION_DIAGNOSTIC_CAPTURE_NO_ORDER_tiny_recovery_capture_current_decision_diagnostic_fields_no_start_no_replay_no_pnl_20260519_102918_next_route_runbook.md
docs/runbooks/LANE-F-R4R14_DIAGNOSTIC_WIRING_PATCH_PLAN_NO_PATCH_NO_START_plan_wiring_runtime_gate_diagnostics_into_decision_output_no_patch_no_start_no_replay_no_pnl_20260519_103156_next_route_runbook.md
docs/runbooks/LANE-F-R4R15B_NO_SIGNAL_CONSTRUCTION_PATH_REVIEW_NO_PATCH_NO_START_find_actual_no_signal_runtime_disabled_item_construction_before_wiring_patch_no_start_no_replay_no_pnl_20260519_103619_next_route_runbook.md
docs/runbooks/LANE-F-R4R15C_EXACT_FUNCTION_WIRING_PATCH_PLAN_RECOVERY_NO_PATCH_NO_START_recover_exact_function_plan_after_broken_paste_no_patch_no_start_no_replay_no_pnl_20260519_105219_next_route_runbook.md
docs/runbooks/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_105909_next_route_runbook.md
docs/runbooks/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_110548_next_route_runbook.md
docs/runbooks/LANE-F-R4R15G_MERGE_DIAGNOSTICS_INTO_RAW_PATCH_PLAN_NO_PATCH_NO_START_plan_exact_raw_merge_diagnostic_wiring_patch_no_patch_no_start_no_replay_no_pnl_20260519_110917_next_route_runbook.md
docs/runbooks/LANE-F-R4R15H_RAW_MERGE_DIAGNOSTIC_WIRING_PATCH_APPROVAL_REQUIRED_patch_activation_raw_merge_runtime_diagnostics_no_start_no_replay_no_pnl_no_order_20260519_224247_next_route_runbook.md
docs/runbooks/LANE-F-R4R15_DIAGNOSTIC_WIRING_PATCH_APPROVAL_REQUIRED_patch_runtime_gate_diagnostics_into_strategy_decision_output_only_no_start_no_replay_no_pnl_no_order_20260519_103327_next_route_runbook.md
docs/runbooks/LANE-F-R4R16_RAW_MERGE_WIRING_STATIC_PROOF_NO_START_static_verify_r4r15h_raw_merge_patch_compile_zero_order_no_start_no_replay_no_pnl_20260519_224330_next_route_runbook.md
docs/runbooks/LANE-F-R4R17A_OBSERVE_ONLY_STRATEGY_RESTART_DECISION_REQUIRED_NO_ORDER_decide_next_live_session_observe_only_restart_needed_for_raw_diagnostic_visibility_no_start_no_replay_no_pnl_20260519_225039_next_live_session_runbook.md
docs/runbooks/LANE-F-R4R17R_TAIL_DECISION_DIAGNOSTIC_VISIBILITY_CAPTURE_NO_ORDER_recover_r4r17_with_tail_based_decision_capture_no_xread_no_start_no_replay_no_pnl_20260519_224820_next_route_runbook.md
docs/runbooks/LANE-F-R4R18AR_RECOVER_AFTERMARKET_HANDOFF_BUNDLE_NO_START_recover_archive_packaging_after_relative_path_error_no_start_no_replay_no_pnl_20260519_231123_next_live_session_r4r18_runbook.md
docs/runbooks/LANE-F-R4R18A_AFTERMARKET_RAW_DIAGNOSTIC_PATCH_HANDOFF_BUNDLE_NO_START_compact_bundle_raw_diagnostic_patch_evidence_next_live_session_no_start_no_replay_no_pnl_20260519_230750_next_live_session_r4r18_runbook.md
docs/runbooks/LANE-F-R4R18B_ORPHAN_MAIN_PROCESS_CLASSIFICATION_NO_START_classify_generic_main_process_after_r4r18_preflight_no_start_no_order_no_replay_no_pnl_20260520_093120_next_route_runbook.md
docs/runbooks/LANE-F-R4R18_OBSERVE_ONLY_STACK_RESTART_PREFLIGHT_NO_START_live_session_preflight_before_observe_only_feeds_features_strategy_restart_no_order_no_replay_no_pnl_20260520_092948_restart_gate_runbook.md
docs/runbooks/LANE-F-R4R19H5_APPROVED_INSTRUMENT_METADATA_REFRESH_NO_ORDER_NO_REPLAY_approved_refresh_nfo_instrument_metadata_after_feeds_stale_failure_no_order_no_replay_no_pnl_20260520_100348_next_route_runbook.md
docs/runbooks/LANE-F-R4R4_DECISION_TAIL_AUDIT_AFTER_NO_LIFECYCLE_NO_PATCH_NO_START_read_only_audit_latest_decisions_after_live_capture_no_candidate_no_replay_no_pnl_20260518_143451_next_route_runbook.md
docs/runbooks/LANE-F-R4R5_STRATEGY_BLOCKER_AUDIT_NO_PATCH_NO_START_read_only_audit_strategy_blockers_after_no_candidate_decisions_no_replay_no_pnl_20260518_143812_next_route_runbook.md
docs/runbooks/LANE-F-R4R6_DATA_QUALITY_BLOCKER_AUDIT_NO_PATCH_NO_START_read_only_audit_stage_data_quality_ok_failed_from_live_features_decisions_no_replay_no_pnl_20260518_144017_next_route_runbook.md
docs/runbooks/LANE-F-R4R7_RUNTIME_ENABLEMENT_SURFACE_AUDIT_NO_PATCH_NO_START_read_only_audit_why_classic_and_miso_runtime_disabled_no_order_no_replay_no_pnl_20260518_144147_next_route_runbook.md
docs/runbooks/LANE-F-R4R8R2_RUNTIME_GATE_MINIMAL_PATCH_PLAN_NO_PATCH_NO_START_minimal_recovery_plan_after_broken_paste_no_live_change_no_replay_no_pnl_20260518_144956_next_route_runbook.md
docs/runbooks/LANE-F-R4R9R_SOURCE_REVIEW_RECOVERY_NO_PATCH_NO_START_compact_runtime_gate_source_review_after_broken_paste_no_replay_no_pnl_20260518_145356_next_route_runbook.md
run/audits/B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133_audit.json
run/audits/B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133_dhan_writer_source_extract.md
run/audits/B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133_pnl_semantics_cost_lot_validation.md
run/audits/B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133_samples/enriched_replay_records_aa13b_r4_input_normalized_economics_derived_first_25.csv
run/audits/B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133_samples/enriched_replay_records_aa13b_r4_input_normalized_economics_derived_nonblank_pnl_50.csv
run/audits/B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133_samples/enriched_replay_records_aa13b_r4_input_normalized_first_25.csv
run/audits/B1-PROFIT-AFTERMARKET-R1_DHAN_WRITER_PNL_SEMANTICS_AND_CONTEXT_SERVICE_DESIGN_NO_ORDER_source_extract_dhan_context_writer_validate_pnl_semantics_and_design_context_service_no_patch_no_start_no_order_20260520_235133_samples/enriched_replay_records_aa13b_r4_input_normalized_nonblank_pnl_50.csv
run/audits/B1-PROFIT-HANDOFF-R0_AFTER_MARKET_STATUS_AND_NEXT_DAY_PLAN_NO_ORDER_consolidate_profitability_pnl_candidate_dhan_status_and_next_day_live_plan_no_patch_no_start_no_order_20260520_234701_audit.json
run/audits/B1-PROFIT-HANDOFF-R0_AFTER_MARKET_STATUS_AND_NEXT_DAY_PLAN_NO_ORDER_consolidate_profitability_pnl_candidate_dhan_status_and_next_day_live_plan_no_patch_no_start_no_order_20260520_234701_status_report.md
run/audits/B1-PROFIT-SIM-R1_RECORDED_CANDIDATE_PNL_PRECHECK_NO_ORDER_after_market_precheck_candidate_pnl_files_from_recorded_inventory_no_start_no_order_20260520_232330_audit.json
run/audits/B1-PROFIT-SIM-R1_RECORDED_CANDIDATE_PNL_PRECHECK_NO_ORDER_after_market_precheck_candidate_pnl_files_from_recorded_inventory_no_start_no_order_20260520_232330_pnl_precheck_report.md
run/audits/B1-PROFIT-SIM-R2_RECORDED_PNL_SUMMARY_NO_ORDER_after_market_summarize_recorded_pnl_csvs_from_r1_precheck_no_start_no_order_20260520_232551_audit.json
run/audits/B1-PROFIT-SIM-R2_RECORDED_PNL_SUMMARY_NO_ORDER_after_market_summarize_recorded_pnl_csvs_from_r1_precheck_no_start_no_order_20260520_232551_recorded_pnl_summary_report.md
run/audits/B1-PROFIT-SIM-R3_PNL_EVIDENCE_DEEP_INSPECTION_NO_ORDER_inspect_recorded_pnl_csv_columns_lot_size_trade_count_duplicate_status_no_start_no_order_20260520_233335_audit.json
run/audits/B1-PROFIT-SIM-R3_PNL_EVIDENCE_DEEP_INSPECTION_NO_ORDER_inspect_recorded_pnl_csv_columns_lot_size_trade_count_duplicate_status_no_start_no_order_20260520_233335_pnl_deep_inspection_report.md
run/audits/B1-PROFIT-SIM-R3_PNL_EVIDENCE_DEEP_INSPECTION_NO_ORDER_inspect_recorded_pnl_csv_columns_lot_size_trade_count_duplicate_status_no_start_no_order_20260520_233335_samples/enriched_replay_records_aa13b_r4_input_normalized_economics_derived_sample_first_50.csv
run/audits/B1-PROFIT-SIM-R3_PNL_EVIDENCE_DEEP_INSPECTION_NO_ORDER_inspect_recorded_pnl_csv_columns_lot_size_trade_count_duplicate_status_no_start_no_order_20260520_233335_samples/enriched_replay_records_aa13b_r4_input_normalized_sample_first_50.csv
run/audits/B1-R26_EXECUTION_SHADOW_SEAM_AUDIT_NO_PATCH_NO_START_locate_execution_shadow_no_broker_seam_20260517_161940_audit.json
run/audits/B1-R27_EXECUTION_SHADOW_BOOTSTRAP_ROUTE_PLAN_NO_PATCH_NO_START_map_existing_execution_shadow_bootstrap_route_20260517_162107_audit.json
run/audits/B1-R29_MAIN_HELPER_SHADOW_ROUTE_BINDING_PATCH_DRY_PROOF_NO_START_bind_observe_only_execution_shadow_no_broker_route_20260517_162549_audit.json
run/audits/B1-R29_MAIN_HELPER_SHADOW_ROUTE_BINDING_PATCH_DRY_PROOF_NO_START_bind_observe_only_execution_shadow_no_broker_route_20260517_162549_patch.diff
run/audits/B1A-R30_RETRY_HELPER_EXECUTE_AFTER_SHADOW_ROUTE_PATCH_APPROVAL_REQUIRED_guarded_helper_execute_after_shadow_route_patch_verify_streams_no_replay_no_pnl_no_order_20260517_164308_audit.json
run/audits/B1A-R30_RETRY_HELPER_EXECUTE_AFTER_SHADOW_ROUTE_PATCH_APPROVAL_REQUIRED_guarded_helper_execute_after_shadow_route_patch_verify_streams_no_replay_no_pnl_no_order_20260517_164308_helper_dry_run.json
run/audits/B1A-R30_RETRY_HELPER_EXECUTE_AFTER_SHADOW_ROUTE_PATCH_APPROVAL_REQUIRED_guarded_helper_execute_after_shadow_route_patch_verify_streams_no_replay_no_pnl_no_order_20260517_164308_helper_execute_report.json
run/audits/B1A-R32_APPLY_HELPER_SERVICE_SELECTION_AND_MAIN_EXECUTION_SHADOW_BINDING_PATCH_NO_START_patch_helper_per_service_selection_and_main_execution_shadow_no_broker_binding_no_start_20260517_165051_audit.json
run/audits/B1A-R32_APPLY_HELPER_SERVICE_SELECTION_AND_MAIN_EXECUTION_SHADOW_BINDING_PATCH_NO_START_patch_helper_per_service_selection_and_main_execution_shadow_no_broker_binding_no_start_20260517_165051_backups/app/mme_scalpx/main.py
run/audits/B1A-R32_APPLY_HELPER_SERVICE_SELECTION_AND_MAIN_EXECUTION_SHADOW_BINDING_PATCH_NO_START_patch_helper_per_service_selection_and_main_execution_shadow_no_broker_binding_no_start_20260517_165051_backups/bin/b1_observe_only_stack_start_helper.py
run/audits/B1A-R32_APPLY_HELPER_SERVICE_SELECTION_AND_MAIN_EXECUTION_SHADOW_BINDING_PATCH_NO_START_patch_helper_per_service_selection_and_main_execution_shadow_no_broker_binding_no_start_20260517_165051_git_diff_main_helper.patch
run/audits/B1A-R32_APPLY_HELPER_SERVICE_SELECTION_AND_MAIN_EXECUTION_SHADOW_BINDING_PATCH_NO_START_patch_helper_per_service_selection_and_main_execution_shadow_no_broker_binding_no_start_20260517_165051_helper_dry_run.json
run/audits/B1A-R32_APPLY_HELPER_SERVICE_SELECTION_AND_MAIN_EXECUTION_SHADOW_BINDING_PATCH_NO_START_patch_helper_per_service_selection_and_main_execution_shadow_no_broker_binding_no_start_20260517_165051_patch_audit.json
run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_audit.json
run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_backups/app/mme_scalpx/core/names.py
run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_backups/app/mme_scalpx/services/execution.py
run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_backups/app/mme_scalpx/services/risk.py
run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_backups/bin/b1_observe_only_stack_start_helper.py
run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_git_diff.patch
run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_helper_dry_run.json
run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_patch_audit.json
run/audits/B1A-R38_LIFECYCLE_TRIGGER_PATCH_APPROVAL_REQUIRED_patch_observe_only_lifecycle_publishers_for_risk_execution_no_start_no_replay_no_pnl_20260517_171410_audit.json
run/audits/B1A-R38_LIFECYCLE_TRIGGER_PATCH_APPROVAL_REQUIRED_patch_observe_only_lifecycle_publishers_for_risk_execution_no_start_no_replay_no_pnl_20260517_171410_patch_audit.json
run/audits/B1A-R41_STATUS_ONLY_LIFECYCLE_ATTESTATION_FOR_B1B_NO_PATCH_NO_START_machine_readable_attestation_lifecycle_rows_status_only_for_b1b_r4d_no_replay_no_pnl_20260517_173407_audit.json
run/audits/B1B-R4A_EXTRACT_B1A_R39_R40R_LIFECYCLE_SCHEMA_NO_PATCH_NO_START_read_only_extract_exact_lifecycle_evidence_fields_after_r4_parser_block_20260517_173108_extract/home/Lenovo/scalpx/projects/mme_scalpx/docs/milestones/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008.md
run/audits/B1B-R4A_EXTRACT_B1A_R39_R40R_LIFECYCLE_SCHEMA_NO_PATCH_NO_START_read_only_extract_exact_lifecycle_evidence_fields_after_r4_parser_block_20260517_173108_extract/home/Lenovo/scalpx/projects/mme_scalpx/docs/runbooks/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_next_execute_runbook.md
run/audits/B1B-R4A_EXTRACT_B1A_R39_R40R_LIFECYCLE_SCHEMA_NO_PATCH_NO_START_read_only_extract_exact_lifecycle_evidence_fields_after_r4_parser_block_20260517_173108_extract/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_audit.json
run/audits/B1B-R4A_EXTRACT_B1A_R39_R40R_LIFECYCLE_SCHEMA_NO_PATCH_NO_START_read_only_extract_exact_lifecycle_evidence_fields_after_r4_parser_block_20260517_173108_extract/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_backups/app/mme_scalpx/core/names.py
run/audits/B1B-R4A_EXTRACT_B1A_R39_R40R_LIFECYCLE_SCHEMA_NO_PATCH_NO_START_read_only_extract_exact_lifecycle_evidence_fields_after_r4_parser_block_20260517_173108_extract/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_backups/app/mme_scalpx/services/execution.py
run/audits/B1B-R4A_EXTRACT_B1A_R39_R40R_LIFECYCLE_SCHEMA_NO_PATCH_NO_START_read_only_extract_exact_lifecycle_evidence_fields_after_r4_parser_block_20260517_173108_extract/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_backups/app/mme_scalpx/services/risk.py
run/audits/B1B-R4A_EXTRACT_B1A_R39_R40R_LIFECYCLE_SCHEMA_NO_PATCH_NO_START_read_only_extract_exact_lifecycle_evidence_fields_after_r4_parser_block_20260517_173108_extract/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_backups/bin/b1_observe_only_stack_start_helper.py
run/audits/B1B-R4A_EXTRACT_B1A_R39_R40R_LIFECYCLE_SCHEMA_NO_PATCH_NO_START_read_only_extract_exact_lifecycle_evidence_fields_after_r4_parser_block_20260517_173108_extract/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_git_diff.patch
run/audits/B1B-R4A_EXTRACT_B1A_R39_R40R_LIFECYCLE_SCHEMA_NO_PATCH_NO_START_read_only_extract_exact_lifecycle_evidence_fields_after_r4_parser_block_20260517_173108_extract/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_helper_dry_run.json
run/audits/B1B-R4A_EXTRACT_B1A_R39_R40R_LIFECYCLE_SCHEMA_NO_PATCH_NO_START_read_only_extract_exact_lifecycle_evidence_fields_after_r4_parser_block_20260517_173108_extract/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_patch_audit.json
run/audits/B1B-R4A_EXTRACT_B1A_R39_R40R_LIFECYCLE_SCHEMA_NO_PATCH_NO_START_read_only_extract_exact_lifecycle_evidence_fields_after_r4_parser_block_20260517_173108_extract/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/B1A-R32_APPLY_HELPER_SERVICE_SELECTION_AND_MAIN_EXECUTION_SHADOW_BINDING_PATCH_NO_START_patch_helper_per_service_selection_and_main_execution_shadow_no_broker_binding_no_start_20260517_165051.json
run/audits/B1B-R4A_EXTRACT_B1A_R39_R40R_LIFECYCLE_SCHEMA_NO_PATCH_NO_START_read_only_extract_exact_lifecycle_evidence_fields_after_r4_parser_block_20260517_173108_extract/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008.json
run/audits/B1B-R4D_ACCEPT_B1A_STATUS_ONLY_ATTESTATION_RUNTIME_LIFECYCLE_ACCEPTED_NO_BACKTEST_NO_PNL_ingest_b1a_r41_attestation_accept_runtime_lifecycle_keep_backtest_not_admitted_pnl_not_ready_20260517_173549_audit.json
run/audits/B1B-R4_INGEST_B1A_R40R_LIFECYCLE_HANDOFF_AND_REFRESH_ADMISSION_MATRIX_NO_REPLAY_NO_PNL_ingest_b1a_r39_r40r_observe_only_lifecycle_evidence_without_admitting_backtest_20260517_173012_extracted_b1a_handoff/home/Lenovo/scalpx/projects/mme_scalpx/docs/milestones/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008.md
run/audits/B1B-R4_INGEST_B1A_R40R_LIFECYCLE_HANDOFF_AND_REFRESH_ADMISSION_MATRIX_NO_REPLAY_NO_PNL_ingest_b1a_r39_r40r_observe_only_lifecycle_evidence_without_admitting_backtest_20260517_173012_extracted_b1a_handoff/home/Lenovo/scalpx/projects/mme_scalpx/docs/runbooks/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_next_execute_runbook.md
run/audits/B1B-R4_INGEST_B1A_R40R_LIFECYCLE_HANDOFF_AND_REFRESH_ADMISSION_MATRIX_NO_REPLAY_NO_PNL_ingest_b1a_r39_r40r_observe_only_lifecycle_evidence_without_admitting_backtest_20260517_173012_extracted_b1a_handoff/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_audit.json
run/audits/B1B-R4_INGEST_B1A_R40R_LIFECYCLE_HANDOFF_AND_REFRESH_ADMISSION_MATRIX_NO_REPLAY_NO_PNL_ingest_b1a_r39_r40r_observe_only_lifecycle_evidence_without_admitting_backtest_20260517_173012_extracted_b1a_handoff/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_backups/app/mme_scalpx/core/names.py
run/audits/B1B-R4_INGEST_B1A_R40R_LIFECYCLE_HANDOFF_AND_REFRESH_ADMISSION_MATRIX_NO_REPLAY_NO_PNL_ingest_b1a_r39_r40r_observe_only_lifecycle_evidence_without_admitting_backtest_20260517_173012_extracted_b1a_handoff/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_backups/app/mme_scalpx/services/execution.py
run/audits/B1B-R4_INGEST_B1A_R40R_LIFECYCLE_HANDOFF_AND_REFRESH_ADMISSION_MATRIX_NO_REPLAY_NO_PNL_ingest_b1a_r39_r40r_observe_only_lifecycle_evidence_without_admitting_backtest_20260517_173012_extracted_b1a_handoff/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_backups/app/mme_scalpx/services/risk.py
run/audits/B1B-R4_INGEST_B1A_R40R_LIFECYCLE_HANDOFF_AND_REFRESH_ADMISSION_MATRIX_NO_REPLAY_NO_PNL_ingest_b1a_r39_r40r_observe_only_lifecycle_evidence_without_admitting_backtest_20260517_173012_extracted_b1a_handoff/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_backups/bin/b1_observe_only_stack_start_helper.py
run/audits/B1B-R4_INGEST_B1A_R40R_LIFECYCLE_HANDOFF_AND_REFRESH_ADMISSION_MATRIX_NO_REPLAY_NO_PNL_ingest_b1a_r39_r40r_observe_only_lifecycle_evidence_without_admitting_backtest_20260517_173012_extracted_b1a_handoff/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_git_diff.patch
run/audits/B1B-R4_INGEST_B1A_R40R_LIFECYCLE_HANDOFF_AND_REFRESH_ADMISSION_MATRIX_NO_REPLAY_NO_PNL_ingest_b1a_r39_r40r_observe_only_lifecycle_evidence_without_admitting_backtest_20260517_173012_extracted_b1a_handoff/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_helper_dry_run.json
run/audits/B1B-R4_INGEST_B1A_R40R_LIFECYCLE_HANDOFF_AND_REFRESH_ADMISSION_MATRIX_NO_REPLAY_NO_PNL_ingest_b1a_r39_r40r_observe_only_lifecycle_evidence_without_admitting_backtest_20260517_173012_extracted_b1a_handoff/home/Lenovo/scalpx/projects/mme_scalpx/run/audits/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008_patch_audit.json
run/audits/B1B-R4_INGEST_B1A_R40R_LIFECYCLE_HANDOFF_AND_REFRESH_ADMISSION_MATRIX_NO_REPLAY_NO_PNL_ingest_b1a_r39_r40r_observe_only_lifecycle_evidence_without_admitting_backtest_20260517_173012_extracted_b1a_handoff/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/B1A-R32_APPLY_HELPER_SERVICE_SELECTION_AND_MAIN_EXECUTION_SHADOW_BINDING_PATCH_NO_START_patch_helper_per_service_selection_and_main_execution_shadow_no_broker_binding_no_start_20260517_165051.json
run/audits/B1B-R4_INGEST_B1A_R40R_LIFECYCLE_HANDOFF_AND_REFRESH_ADMISSION_MATRIX_NO_REPLAY_NO_PNL_ingest_b1a_r39_r40r_observe_only_lifecycle_evidence_without_admitting_backtest_20260517_173012_extracted_b1a_handoff/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/B1A-R38D_NAMES_AND_LIFECYCLE_SOURCE_PATCH_APPROVAL_REQUIRED_patch_names_stream_constants_and_observe_only_lifecycle_publishers_no_start_no_replay_no_pnl_20260517_172008.json
run/audits/B1B-R5_BACKTEST_ADMISSION_REMAINS_NOT_ADMITTED_PENDING_VALID_TRADE_LIFECYCLE_freeze_runtime_lifecycle_accepted_but_backtest_pnl_blocked_until_valid_trade_lifecycle_no_patch_no_start_20260517_173722_audit.json
run/audits/B3-R10_FIX_FEATURE_DECISION_DATASET_LAYOUT_NO_ORDER_stage_opt_ticks_required_and_features_decisions_optional_then_test_valid_replay_scopes_no_broker_order_pnl_20260521_125540_audit.json
run/audits/B3-R11_ONE_STRATEGY_DETERMINISTIC_DRY_REPLAY_NO_ORDER_run_two_deterministic_feeds_features_strategy_dry_replays_for_mist_call_no_broker_order_pnl_20260521_133642_audit.json
run/audits/B3-R1_LIVE_DATASET_ADMISSION_AUDIT_NO_START_NO_REPLAY_NO_ORDER_audit_existing_live_streams_for_replay_dataset_admission_without_start_stop_replay_order_pnl_20260521_101008_audit.json
run/audits/B3-R25A_REPLAY_ROW_SURFACE_DEEP_AUDIT_NO_PATCH_NO_REPLAY_NO_ORDER_inspect_strategy_decisions_features_rows_risk_execution_shadow_for_candidate_blocker_economics_fields_20260528_231726_audit.json
run/audits/B3-R3_OFFLINE_REPLAY_DRY_RUN_FROM_CAPTURED_SURFACES_ZERODHA_ONLY_NO_BROKER_NO_ORDER_run_or_block_offline_replay_mvp_dry_run_from_b3_r2_manifest_without_broker_order_pnl_20260521_102211_audit.json
run/audits/B3-R4_DETERMINISTIC_OFFLINE_REPLAY_EXECUTION_DRY_ONLY_NO_BROKER_NO_ORDER_run_deterministic_offline_replay_cli_dry_only_from_mvp_dataset_no_broker_order_pnl_20260521_102417_audit.json
run/audits/B3-R9_ONE_STRATEGY_DRY_REPLAY_COMPATIBILITY_CHECK_NO_ORDER_check_replay_cli_strategy_stage_compatibility_using_b3_r8_mist_call_adapter_no_broker_order_pnl_20260521_125333_audit.json
run/audits/LANE-F-R0_VALID_TRADE_LIFECYCLE_EVIDENCE_INVENTORY_NO_PATCH_NO_START_read_only_inventory_for_valid_trade_lifecycle_data_after_b1b_r5_wait_state_no_replay_no_pnl_20260517_173947_audit.json
run/audits/LANE-F-R0_VALID_TRADE_LIFECYCLE_EVIDENCE_INVENTORY_NO_PATCH_NO_START_read_only_inventory_for_valid_trade_lifecycle_data_after_b1b_r5_wait_state_no_replay_no_pnl_20260517_173947_inventory.md
run/audits/LANE-F-R1_VALIDATE_CANDIDATE_LIFECYCLE_FILES_NO_REPLAY_NO_PNL_read_only_validate_possible_lifecycle_candidate_files_from_lane_f_r0_no_admission_no_replay_no_pnl_20260517_174249_audit.json
run/audits/LANE-F-R1_VALIDATE_CANDIDATE_LIFECYCLE_FILES_NO_REPLAY_NO_PNL_read_only_validate_possible_lifecycle_candidate_files_from_lane_f_r0_no_admission_no_replay_no_pnl_20260517_174249_validation.md
run/audits/LANE-F-R2_CAPTURE_PLAN_FOR_FUTURE_VALID_TRADE_LIFECYCLE_DATA_NO_START_freeze_future_live_session_valid_trade_lifecycle_capture_plan_no_patch_no_start_no_replay_no_pnl_20260517_174422_audit.json
run/audits/LANE-F-R4R10_RUNTIME_GATE_PATCH_PLAN_NO_PATCH_NO_START_after_market_deep_patch_plan_for_family_runtime_disabled_gate_no_patch_no_start_no_replay_no_pnl_20260518_150607_audit.json
run/audits/LANE-F-R4R10_RUNTIME_GATE_PATCH_PLAN_NO_PATCH_NO_START_after_market_deep_patch_plan_for_family_runtime_disabled_gate_no_patch_no_start_no_replay_no_pnl_20260518_150607_patch_plan.md
run/audits/LANE-F-R4R10_RUNTIME_GATE_PATCH_PLAN_NO_PATCH_NO_START_after_market_deep_patch_plan_for_family_runtime_disabled_gate_no_patch_no_start_no_replay_no_pnl_20260518_150607_source_extract.txt
run/audits/LANE-F-R4R12_DIAGNOSTIC_PATCH_STATIC_PROOF_NO_START_static_verify_r4r11r_diagnostic_helpers_compile_zero_order_no_start_no_replay_no_pnl_20260518_152329_audit.json
run/audits/LANE-F-R4R12_DIAGNOSTIC_PATCH_STATIC_PROOF_NO_START_static_verify_r4r11r_diagnostic_helpers_compile_zero_order_no_start_no_replay_no_pnl_20260518_152329_static_proof.md
run/audits/LANE-F-R4R13R2_TINY_LIVE_DECISION_DIAGNOSTIC_CAPTURE_NO_ORDER_tiny_recovery_capture_current_decision_diagnostic_fields_no_start_no_replay_no_pnl_20260519_102918_audit.json
run/audits/LANE-F-R4R14_DIAGNOSTIC_WIRING_PATCH_PLAN_NO_PATCH_NO_START_plan_wiring_runtime_gate_diagnostics_into_decision_output_no_patch_no_start_no_replay_no_pnl_20260519_103156_audit.json
run/audits/LANE-F-R4R14_DIAGNOSTIC_WIRING_PATCH_PLAN_NO_PATCH_NO_START_plan_wiring_runtime_gate_diagnostics_into_decision_output_no_patch_no_start_no_replay_no_pnl_20260519_103156_patch_plan.md
run/audits/LANE-F-R4R14_DIAGNOSTIC_WIRING_PATCH_PLAN_NO_PATCH_NO_START_plan_wiring_runtime_gate_diagnostics_into_decision_output_no_patch_no_start_no_replay_no_pnl_20260519_103156_source_extract.txt
run/audits/LANE-F-R4R15B_NO_SIGNAL_CONSTRUCTION_PATH_REVIEW_NO_PATCH_NO_START_find_actual_no_signal_runtime_disabled_item_construction_before_wiring_patch_no_start_no_replay_no_pnl_20260519_103619_audit.json
run/audits/LANE-F-R4R15B_NO_SIGNAL_CONSTRUCTION_PATH_REVIEW_NO_PATCH_NO_START_find_actual_no_signal_runtime_disabled_item_construction_before_wiring_patch_no_start_no_replay_no_pnl_20260519_103619_construction_path_review.md
run/audits/LANE-F-R4R15B_NO_SIGNAL_CONSTRUCTION_PATH_REVIEW_NO_PATCH_NO_START_find_actual_no_signal_runtime_disabled_item_construction_before_wiring_patch_no_start_no_replay_no_pnl_20260519_103619_source_extract.txt
run/audits/LANE-F-R4R15C_EXACT_FUNCTION_WIRING_PATCH_PLAN_RECOVERY_NO_PATCH_NO_START_recover_exact_function_plan_after_broken_paste_no_patch_no_start_no_replay_no_pnl_20260519_105219_audit.json
run/audits/LANE-F-R4R15C_EXACT_FUNCTION_WIRING_PATCH_PLAN_RECOVERY_NO_PATCH_NO_START_recover_exact_function_plan_after_broken_paste_no_patch_no_start_no_replay_no_pnl_20260519_105219_evaluation_to_frame_extract.txt
run/audits/LANE-F-R4R15C_EXACT_FUNCTION_WIRING_PATCH_PLAN_RECOVERY_NO_PATCH_NO_START_recover_exact_function_plan_after_broken_paste_no_patch_no_start_no_replay_no_pnl_20260519_105219_patch_plan.md
run/audits/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_105909_audit.json
run/audits/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_105909_definition_discovery.md
run/audits/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_105909_source_extract.txt
run/audits/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_110548_audit.json
run/audits/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_110548_definition_discovery.md
run/audits/LANE-F-R4R15F_DOCTRINE_EVALUATION_FRAME_DEFINITION_DISCOVERY_NO_PATCH_NO_START_discover_doctrine_evaluation_frame_definition_and_import_surface_no_patch_no_start_no_replay_no_pnl_20260519_110548_source_extract.txt
run/audits/LANE-F-R4R15G_MERGE_DIAGNOSTICS_INTO_RAW_PATCH_PLAN_NO_PATCH_NO_START_plan_exact_raw_merge_diagnostic_wiring_patch_no_patch_no_start_no_replay_no_pnl_20260519_110917_audit.json
run/audits/LANE-F-R4R15G_MERGE_DIAGNOSTICS_INTO_RAW_PATCH_PLAN_NO_PATCH_NO_START_plan_exact_raw_merge_diagnostic_wiring_patch_no_patch_no_start_no_replay_no_pnl_20260519_110917_evaluation_to_frame_extract.txt
run/audits/LANE-F-R4R15G_MERGE_DIAGNOSTICS_INTO_RAW_PATCH_PLAN_NO_PATCH_NO_START_plan_exact_raw_merge_diagnostic_wiring_patch_no_patch_no_start_no_replay_no_pnl_20260519_110917_patch_plan.md
run/audits/LANE-F-R4R15H_RAW_MERGE_DIAGNOSTIC_WIRING_PATCH_APPROVAL_REQUIRED_patch_activation_raw_merge_runtime_diagnostics_no_start_no_replay_no_pnl_no_order_20260519_224247_audit.json

## Existing risk/execution-shadow output artifacts, if any
run/replay/_phase_a4_comparability_gate_check/04_metrics_summary.json
run/replay/_phase_a4_comparability_gate_check/shadow_override_flattened.json
run/replay/_phase_a4_dataset_summary_guard_real_check/baseline_frames.json
run/replay/_phase_a4_dataset_summary_guard_real_check/shadow_frames.json
run/replay/_phase_a4_dataset_summary_guard_smoke/01_dataset_summary.json
run/replay/_phase_a4_dataset_summary_guard_smoke/artifacts/features_rows.json
run/replay/_phase_a4_dataset_summary_guard_smoke/artifacts/strategy_decisions.json
run/replay/_phase_a4_dataset_summary_guard_v2_real_check/baseline_frames.json
run/replay/_phase_a4_dataset_summary_guard_v2_real_check/shadow_frames.json
run/replay/_phase_a4_dataset_summary_guard_v3_real_check/baseline_frames.json
run/replay/_phase_a4_dataset_summary_guard_v3_real_check/shadow_frames.json
run/replay/_phase_a4_declared_alias_normalization_real_check/shadow_frames.json
run/replay/_phase_a4_observed_source_fields_real_check/shadow_frames.json
run/replay/_phase_a4_observed_source_fields_v2_real_check/shadow_frames.json
run/replay/_phase_a4_refresh_dataset_summary_real_check/baseline_frames.json
run/replay/_phase_a4_refresh_dataset_summary_real_check/shadow_frames.json
run/replay/_phase_a4_replay_compare_insufficiency_check/04_metrics_summary.json
run/replay/_phase_a4_replay_compare_insufficiency_check/shadow_override_flattened.json
run/replay/_phase_a4_row_context_overlay_compare_check/04_metrics_summary.json
run/replay/_phase_a4_row_context_overlay_compare_check/shadow_override_flattened.json
run/replay/_phase_a4_row_context_overlay_real_check/shadow_frames.json
run/replay/_phase_a4_true_owner_rerun_export_check/shadow_frames.json
run/replay/_phase_a4_truth_passthrough_export_check/shadow_frames.json
run/replay/_phase_a4_truth_passthrough_v2_export_check/shadow_frames.json
run/replay/a38_declaration_smoke/replay_data_a38_20260510T043850Z/replay_locked_single_day_a38_declaration_aware_feeds_only_smoke_20260510_043855_3c7771fd/01_dataset_summary.json
run/replay/a38_declaration_smoke/replay_data_a38_20260510T043850Z/replay_locked_single_day_a38_declaration_aware_feeds_only_smoke_20260510_043855_3c7771fd/04_metrics_summary.json
run/replay/a38_declaration_smoke/replay_data_a38_20260510T043850Z/replay_locked_single_day_a38_declaration_aware_feeds_only_smoke_20260510_043855_3c7771fd/artifacts/10_run_summary.json
run/replay/a38_declaration_smoke/replay_data_a38_20260510T043850Z/replay_locked_single_day_a38_declaration_aware_feeds_only_smoke_20260510_043855_3c7771fd/artifacts/11_run_summary.csv
run/replay/a38_declaration_smoke/replay_data_a38_20260510T043850Z/replay_locked_single_day_a38_declaration_aware_feeds_only_smoke_20260510_043855_3c7771fd/artifacts/execution_shadow_results.json
run/replay/a38_declaration_smoke/replay_data_a38_20260510T043850Z/replay_locked_single_day_a38_declaration_aware_feeds_only_smoke_20260510_043855_3c7771fd/artifacts/risk_outputs.json
run/replay/a41_declaration_smoke/replay_data_a41_20260510T044459Z/replay_locked_single_day_a41_declaration_aware_feeds_only_smoke_20260510_044503_d74e802d/01_dataset_summary.json
run/replay/a41_declaration_smoke/replay_data_a41_20260510T044459Z/replay_locked_single_day_a41_declaration_aware_feeds_only_smoke_20260510_044503_d74e802d/04_metrics_summary.json
run/replay/a41_declaration_smoke/replay_data_a41_20260510T044459Z/replay_locked_single_day_a41_declaration_aware_feeds_only_smoke_20260510_044503_d74e802d/artifacts/10_run_summary.json
run/replay/a41_declaration_smoke/replay_data_a41_20260510T044459Z/replay_locked_single_day_a41_declaration_aware_feeds_only_smoke_20260510_044503_d74e802d/artifacts/11_run_summary.csv
run/replay/a41_declaration_smoke/replay_data_a41_20260510T044459Z/replay_locked_single_day_a41_declaration_aware_feeds_only_smoke_20260510_044503_d74e802d/artifacts/execution_shadow_results.json
run/replay/a41_declaration_smoke/replay_data_a41_20260510T044459Z/replay_locked_single_day_a41_declaration_aware_feeds_only_smoke_20260510_044503_d74e802d/artifacts/risk_outputs.json
run/replay/a44_declaration_smoke/replay_data_a44_20260510T050911Z/replay_locked_single_day_a44_declaration_aware_feeds_only_smoke_20260510_050916_ede7c439/01_dataset_summary.json
run/replay/a44_declaration_smoke/replay_data_a44_20260510T050911Z/replay_locked_single_day_a44_declaration_aware_feeds_only_smoke_20260510_050916_ede7c439/04_metrics_summary.json
run/replay/a44_declaration_smoke/replay_data_a44_20260510T050911Z/replay_locked_single_day_a44_declaration_aware_feeds_only_smoke_20260510_050916_ede7c439/artifacts/10_run_summary.json
run/replay/a44_declaration_smoke/replay_data_a44_20260510T050911Z/replay_locked_single_day_a44_declaration_aware_feeds_only_smoke_20260510_050916_ede7c439/artifacts/11_run_summary.csv
run/replay/a44_declaration_smoke/replay_data_a44_20260510T050911Z/replay_locked_single_day_a44_declaration_aware_feeds_only_smoke_20260510_050916_ede7c439/artifacts/execution_shadow_results.json
run/replay/a44_declaration_smoke/replay_data_a44_20260510T050911Z/replay_locked_single_day_a44_declaration_aware_feeds_only_smoke_20260510_050916_ede7c439/artifacts/risk_outputs.json
run/replay/a47_declaration_smoke/replay_data_a47_20260510T051518Z/replay_locked_single_day_a47_declaration_aware_feeds_only_smoke_20260510_051522_35fdff7f/01_dataset_summary.json
run/replay/a47_declaration_smoke/replay_data_a47_20260510T051518Z/replay_locked_single_day_a47_declaration_aware_feeds_only_smoke_20260510_051522_35fdff7f/04_metrics_summary.json
run/replay/a47_declaration_smoke/replay_data_a47_20260510T051518Z/replay_locked_single_day_a47_declaration_aware_feeds_only_smoke_20260510_051522_35fdff7f/artifacts/10_run_summary.json
run/replay/a47_declaration_smoke/replay_data_a47_20260510T051518Z/replay_locked_single_day_a47_declaration_aware_feeds_only_smoke_20260510_051522_35fdff7f/artifacts/11_run_summary.csv
run/replay/a47_declaration_smoke/replay_data_a47_20260510T051518Z/replay_locked_single_day_a47_declaration_aware_feeds_only_smoke_20260510_051522_35fdff7f/artifacts/execution_shadow_results.json
run/replay/a47_declaration_smoke/replay_data_a47_20260510T051518Z/replay_locked_single_day_a47_declaration_aware_feeds_only_smoke_20260510_051522_35fdff7f/artifacts/risk_outputs.json
run/replay/a47_declaration_smoke/replay_data_a47_20260510T051550Z/replay_locked_single_day_a47_declaration_aware_feeds_only_smoke_20260510_051554_2d49c653/01_dataset_summary.json
run/replay/a47_declaration_smoke/replay_data_a47_20260510T051550Z/replay_locked_single_day_a47_declaration_aware_feeds_only_smoke_20260510_051554_2d49c653/04_metrics_summary.json
run/replay/a47_declaration_smoke/replay_data_a47_20260510T051550Z/replay_locked_single_day_a47_declaration_aware_feeds_only_smoke_20260510_051554_2d49c653/artifacts/10_run_summary.json
run/replay/a47_declaration_smoke/replay_data_a47_20260510T051550Z/replay_locked_single_day_a47_declaration_aware_feeds_only_smoke_20260510_051554_2d49c653/artifacts/11_run_summary.csv
run/replay/a47_declaration_smoke/replay_data_a47_20260510T051550Z/replay_locked_single_day_a47_declaration_aware_feeds_only_smoke_20260510_051554_2d49c653/artifacts/execution_shadow_results.json
run/replay/a47_declaration_smoke/replay_data_a47_20260510T051550Z/replay_locked_single_day_a47_declaration_aware_feeds_only_smoke_20260510_051554_2d49c653/artifacts/risk_outputs.json
run/replay/a51_declaration_smoke/replay_data_a51_20260510T052726Z/replay_locked_single_day_a51_declaration_aware_feeds_only_smoke_20260510_052731_fbbc69c8/01_dataset_summary.json
run/replay/a51_declaration_smoke/replay_data_a51_20260510T052726Z/replay_locked_single_day_a51_declaration_aware_feeds_only_smoke_20260510_052731_fbbc69c8/04_metrics_summary.json
run/replay/a51_declaration_smoke/replay_data_a51_20260510T052726Z/replay_locked_single_day_a51_declaration_aware_feeds_only_smoke_20260510_052731_fbbc69c8/artifacts/10_run_summary.json
run/replay/a51_declaration_smoke/replay_data_a51_20260510T052726Z/replay_locked_single_day_a51_declaration_aware_feeds_only_smoke_20260510_052731_fbbc69c8/artifacts/11_run_summary.csv
run/replay/a51_declaration_smoke/replay_data_a51_20260510T052726Z/replay_locked_single_day_a51_declaration_aware_feeds_only_smoke_20260510_052731_fbbc69c8/artifacts/execution_shadow_results.json
run/replay/a51_declaration_smoke/replay_data_a51_20260510T052726Z/replay_locked_single_day_a51_declaration_aware_feeds_only_smoke_20260510_052731_fbbc69c8/artifacts/risk_outputs.json
run/replay/a53_command_previews/replay_data_a53_20260510T060003Z/execution_shadow_PREVIEW_ONLY_NOT_EXECUTED.sh
run/replay/a54_feature_scope_gate/replay_data_a54_r2_20260510T060356Z/feature_scope_execution_gate_A55_DO_NOT_RUN_AUTOMATICALLY.json
run/replay/a57_feeds_features_gate/replay_data_a57_r2_20260510T062157Z/feeds_features_execution_gate_A58_DO_NOT_RUN_AUTOMATICALLY.json
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/00_manifest.json
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/01_dataset_summary.json
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/02_scope_profile.json
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/03_integrity_report.json
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/04_metrics_summary.json
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/17_effective_inputs.json
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/18_effective_overrides_flat.json
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/artifacts/10_run_summary.json
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/artifacts/11_run_summary.csv
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/artifacts/engine_result.json
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/artifacts/execution_shadow_results.json
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/artifacts/features_rows.json
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/artifacts/risk_outputs.json
run/replay/a58_feeds_features_execution/replay_data_a58_20260510T062600Z/replay_locked_single_day_a58_durable_feeds_features_execution_20260510_062605_f7ed5e6d/artifacts/strategy_decisions.json
run/replay/a60_feeds_features_strategy_gate/replay_data_a60_20260510T063238Z/feeds_features_strategy_execution_gate_A61_DO_NOT_RUN_AUTOMATICALLY.json
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/00_manifest.json
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/01_dataset_summary.json
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/02_scope_profile.json
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/03_integrity_report.json
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/04_metrics_summary.json
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/17_effective_inputs.json
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/18_effective_overrides_flat.json
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/artifacts/10_run_summary.json
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/artifacts/11_run_summary.csv
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/artifacts/engine_result.json
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/artifacts/execution_shadow_results.json
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/artifacts/features_rows.json
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/artifacts/risk_outputs.json
run/replay/a61_feeds_features_strategy_execution/replay_data_a61_20260510T063603Z/replay_locked_single_day_a61_durable_feeds_features_strategy_execution_20260510_063607_0df0920d/artifacts/strategy_decisions.json
run/replay/a62_risk_scope_precheck/replay_data_a62_20260510T064052Z/feeds_features_strategy_risk_PREVIEW_ONLY_NOT_EXECUTED.sh
run/replay/a63_r4_feeds_features_strategy_risk_gate/20260510T074544Z/A64_DIRECT_COMMAND_DO_NOT_RUN_UNTIL_LANE_C_CLEARED.sh
run/replay/a63_r4_feeds_features_strategy_risk_gate/20260510T074544Z/A64_DURABLE_RUNNER_DO_NOT_RUN_UNTIL_LANE_C_CLEARED.sh
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/logs/a64_replay_run.log
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/logs/a64_replay_run.pid
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/00_manifest.json
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/01_dataset_summary.json
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/02_scope_profile.json
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/03_integrity_report.json
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/04_metrics_summary.json
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/17_effective_inputs.json
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/18_effective_overrides_flat.json
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/10_run_summary.json
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/11_run_summary.csv
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/engine_result.json
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/execution_shadow_results.json
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/features_rows.json
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/risk_outputs.json
run/replay/a64_feeds_features_strategy_risk_execution/replay_data_a64_after_r5bi_shape_tolerant_clearance_20260510T140201Z/replay_locked_single_day_a64_durable_feeds_features_strategy_risk_execution_after_r5bi_shape_tolerant_clearance_20260510_140312_c7064e92/artifacts/strategy_decisions.json
run/replay/a65_r2_execution_shadow_scope_precheck/20260510T142256Z/feeds_features_strategy_risk_execution_shadow_PREVIEW_ONLY_NOT_EXECUTED.sh
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/A66_DIRECT_EXECUTION_SHADOW_COMMAND.sh
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/A66_DURABLE_EXECUTION_SHADOW_RUNNER.sh
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/logs/a66_replay_run.log
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/logs/a66_replay_run.pid
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/00_manifest.json
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/01_dataset_summary.json
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/02_scope_profile.json
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/03_integrity_report.json
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/04_metrics_summary.json
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/17_effective_inputs.json
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/18_effective_overrides_flat.json
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/artifacts/10_run_summary.json
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/artifacts/11_run_summary.csv
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/artifacts/engine_result.json
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/artifacts/execution_shadow_results.json
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/artifacts/features_rows.json
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/artifacts/risk_outputs.json
run/replay/a66_feeds_features_strategy_risk_execution_shadow_execution/replay_data_a66_from_a65_r2_20260510T142418Z/replay_locked_single_day_a66_guarded_execution_shadow_after_a65_r2_20260510_142422_5faed39e/artifacts/strategy_decisions.json
run/replay/a80_economics_plumbing_dry_run/20260510T154623Z/artifacts/economics_plumbing_summary.json
run/replay/b3_r21/B3-R21_REPLAY_KNOWN_NONEMPTY_R15B_DATASET_NO_PATCH_NO_START_NO_ORDER_run_replay_against_b3_r15b_nonempty_real_capture_dataset_and_audit_outputs_20260527_005827/replay_locked_single_day_b3-r21_replay_known_nonempty_r15b_dataset_no_patch_no_start_no_order_run_replay_against_b3_r15b_nonempty_real_capture_dataset_and_audit_outputs_20260527_005827_20260526_192830_b1431b09/01_dataset_summary.json
run/replay/b3_r21/B3-R21_REPLAY_KNOWN_NONEMPTY_R15B_DATASET_NO_PATCH_NO_START_NO_ORDER_run_replay_against_b3_r15b_nonempty_real_capture_dataset_and_audit_outputs_20260527_005827/replay_locked_single_day_b3-r21_replay_known_nonempty_r15b_dataset_no_patch_no_start_no_order_run_replay_against_b3_r15b_nonempty_real_capture_dataset_and_audit_outputs_20260527_005827_20260526_192830_b1431b09/04_metrics_summary.json
run/replay/b3_r21/B3-R21_REPLAY_KNOWN_NONEMPTY_R15B_DATASET_NO_PATCH_NO_START_NO_ORDER_run_replay_against_b3_r15b_nonempty_real_capture_dataset_and_audit_outputs_20260527_005827/replay_locked_single_day_b3-r21_replay_known_nonempty_r15b_dataset_no_patch_no_start_no_order_run_replay_against_b3_r15b_nonempty_real_capture_dataset_and_audit_outputs_20260527_005827_20260526_192830_b1431b09/artifacts/10_run_summary.json
run/replay/b3_r21/B3-R21_REPLAY_KNOWN_NONEMPTY_R15B_DATASET_NO_PATCH_NO_START_NO_ORDER_run_replay_against_b3_r15b_nonempty_real_capture_dataset_and_audit_outputs_20260527_005827/replay_locked_single_day_b3-r21_replay_known_nonempty_r15b_dataset_no_patch_no_start_no_order_run_replay_against_b3_r15b_nonempty_real_capture_dataset_and_audit_outputs_20260527_005827_20260526_192830_b1431b09/artifacts/11_run_summary.csv
run/replay/b3_r21/B3-R21_REPLAY_KNOWN_NONEMPTY_R15B_DATASET_NO_PATCH_NO_START_NO_ORDER_run_replay_against_b3_r15b_nonempty_real_capture_dataset_and_audit_outputs_20260527_005827/replay_locked_single_day_b3-r21_replay_known_nonempty_r15b_dataset_no_patch_no_start_no_order_run_replay_against_b3_r15b_nonempty_real_capture_dataset_and_audit_outputs_20260527_005827_20260526_192830_b1431b09/artifacts/execution_shadow_results.json
run/replay/b3_r21/B3-R21_REPLAY_KNOWN_NONEMPTY_R15B_DATASET_NO_PATCH_NO_START_NO_ORDER_run_replay_against_b3_r15b_nonempty_real_capture_dataset_and_audit_outputs_20260527_005827/replay_locked_single_day_b3-r21_replay_known_nonempty_r15b_dataset_no_patch_no_start_no_order_run_replay_against_b3_r15b_nonempty_real_capture_dataset_and_audit_outputs_20260527_005827_20260526_192830_b1431b09/artifacts/risk_outputs.json
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/00_manifest.json
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/01_dataset_summary.json
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/02_scope_profile.json
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/03_integrity_report.json
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/04_metrics_summary.json
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/17_effective_inputs.json
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/18_effective_overrides_flat.json
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/artifacts/10_run_summary.json
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/artifacts/11_run_summary.csv
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/artifacts/engine_result.json
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/artifacts/execution_shadow_results.json
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/artifacts/features_rows.json
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/artifacts/risk_outputs.json
run/replay/b3_r24g/B3-R24G_REPLAY_R37M_SLIM_DATASET_AFTER_SEQUENCE_PATCH_NO_ORDER_NO_RISK_EXECUTION_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352/replay_locked_single_day_b3-r24g_replay_r37m_slim_dataset_after_sequence_patch_no_order_no_risk_execution_retry_feeds_features_strategy_replay_after_event_time_sort_and_sequence_id_normalization_20260528_231352_20260528_174353_37b044de/artifacts/strategy_decisions.json
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/00_manifest.json
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/01_dataset_summary.json
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/02_scope_profile.json
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/03_integrity_report.json
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/04_metrics_summary.json
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/17_effective_inputs.json
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/18_effective_overrides_flat.json
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/artifacts/10_run_summary.json
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/artifacts/11_run_summary.csv
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/artifacts/engine_result.json
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/artifacts/execution_shadow_results.json
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/artifacts/features_rows.json
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/artifacts/risk_outputs.json
run/replay/b3_r33/B3-R33_REPLAY_EXPORTS_SMOKE_TEST_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039/replay_locked_single_day_b3-r33_replay_exports_smoke_test_no_redis_no_order_no_risk_execution_run_offline_replay_on_r23b_slim_dataset_verify_r32_exports_exist_and_row_counts_20260531_211039_20260531_154041_6beb06bf/artifacts/strategy_decisions.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/00_manifest.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/01_dataset_summary.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/02_scope_profile.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/03_integrity_report.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/04_metrics_summary.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/06_candidate_audit.csv
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/17_effective_inputs.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/18_effective_overrides_flat.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/10_run_summary.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/11_run_summary.csv
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/b3_r32_analysis_exports_status.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/blocker_distribution.csv
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/economics_summary.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/engine_result.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/execution_shadow_results.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/family_side_summary.csv
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/features_rows.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/risk_outputs.json
run/replay/b3_r35/B3-R35_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R34_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058/replay_locked_single_day_b3-r35_replay_exports_smoke_test_after_r34_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r34_verify_r32_exports_exist_status_ok_and_counts_match_20260531_212058_20260531_155100_818293ea/artifacts/strategy_decisions.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/00_manifest.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/01_dataset_summary.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/02_scope_profile.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/03_integrity_report.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/04_metrics_summary.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/06_candidate_audit.csv
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/17_effective_inputs.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/18_effective_overrides_flat.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/artifacts/10_run_summary.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/artifacts/11_run_summary.csv
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/artifacts/b3_r32_analysis_exports_status.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/artifacts/blocker_distribution.csv
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/artifacts/economics_summary.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/artifacts/engine_result.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/artifacts/execution_shadow_results.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/artifacts/family_side_summary.csv
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/artifacts/features_rows.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/artifacts/risk_outputs.json
run/replay/b3_r37/B3-R37_REPLAY_EXPORTS_SMOKE_TEST_AFTER_R36A_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012/replay_locked_single_day_b3-r37_replay_exports_smoke_test_after_r36a_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r36a_verify_late_exports_have_rows_and_candidate_count_matches_20260531_213012_20260531_160013_93120905/artifacts/strategy_decisions.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/00_manifest.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/01_dataset_summary.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/02_scope_profile.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/03_integrity_report.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/04_metrics_summary.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/06_candidate_audit.csv
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/17_effective_inputs.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/18_effective_overrides_flat.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/artifacts/10_run_summary.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/artifacts/11_run_summary.csv
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/artifacts/b3_r32_analysis_exports_status.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/artifacts/blocker_distribution.csv
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/artifacts/economics_summary.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/artifacts/engine_result.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/artifacts/execution_shadow_results.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/artifacts/family_side_summary.csv
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/artifacts/features_rows.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/artifacts/risk_outputs.json
run/replay/b3_r44/B3-R44_ECONOMICS_ENRICHMENT_SMOKE_AFTER_R43_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243/replay_locked_single_day_b3-r44_economics_enrichment_smoke_after_r43_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r43_verify_economics_summary_enrichment_fields_and_counts_20260531_215243_20260531_162245_3f13302f/artifacts/strategy_decisions.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/00_manifest.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/01_dataset_summary.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/02_scope_profile.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/03_integrity_report.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/04_metrics_summary.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/06_candidate_audit.csv
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/17_effective_inputs.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/18_effective_overrides_flat.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/artifacts/10_run_summary.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/artifacts/11_run_summary.csv
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/artifacts/b3_r32_analysis_exports_status.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/artifacts/blocker_distribution.csv
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/artifacts/economics_summary.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/artifacts/engine_result.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/artifacts/execution_shadow_results.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/artifacts/family_side_summary.csv
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/artifacts/features_rows.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/artifacts/risk_outputs.json
run/replay/b3_r47/B3-R47_ECONOMICS_AUTHORITY_FILTER_SMOKE_AFTER_R46_NO_REDIS_NO_ORDER_NO_RISK_EXECUTION_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902/replay_locked_single_day_b3-r47_economics_authority_filter_smoke_after_r46_no_redis_no_order_no_risk_execution_rerun_offline_replay_after_r46_verify_nonzero_economics_enrichment_matches_r45_expected_values_20260531_223902_20260531_170903_67bfca42/artifacts/strategy_decisions.json
run/replay/b3_r54/B3-R54_DATE_RANGE_AGGREGATE_HELPER_MANUAL_SMOKE_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_execute_r53_helper_against_existing_r47_run_dir_and_verify_aggregate_outputs_20260531_230917/date_range_aggregate/combined_candidate_audit.csv
run/replay/b3_r54/B3-R54_DATE_RANGE_AGGREGATE_HELPER_MANUAL_SMOKE_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_execute_r53_helper_against_existing_r47_run_dir_and_verify_aggregate_outputs_20260531_230917/date_range_aggregate/combined_economics_summary.json
run/replay/b3_r54/B3-R54_DATE_RANGE_AGGREGATE_HELPER_MANUAL_SMOKE_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_execute_r53_helper_against_existing_r47_run_dir_and_verify_aggregate_outputs_20260531_230917/date_range_aggregate/combined_family_side_summary.csv
run/replay/b3_r54/B3-R54_DATE_RANGE_AGGREGATE_HELPER_MANUAL_SMOKE_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_execute_r53_helper_against_existing_r47_run_dir_and_verify_aggregate_outputs_20260531_230917/date_range_aggregate/per_day_summary.csv
run/replay/b3_r57/B3-R57_AGGREGATE_HELPER_SMOKE_AFTER_R56_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_rerun_manual_helper_after_r56_verify_candidate_rows_and_combined_aggregate_counts_20260531_232628/date_range_aggregate/combined_candidate_audit.csv
run/replay/b3_r57/B3-R57_AGGREGATE_HELPER_SMOKE_AFTER_R56_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_rerun_manual_helper_after_r56_verify_candidate_rows_and_combined_aggregate_counts_20260531_232628/date_range_aggregate/combined_economics_summary.json
run/replay/b3_r57/B3-R57_AGGREGATE_HELPER_SMOKE_AFTER_R56_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_rerun_manual_helper_after_r56_verify_candidate_rows_and_combined_aggregate_counts_20260531_232628/date_range_aggregate/combined_family_side_summary.csv
run/replay/b3_r57/B3-R57_AGGREGATE_HELPER_SMOKE_AFTER_R56_NO_REDIS_NO_PATCH_NO_REPLAY_NO_ORDER_rerun_manual_helper_after_r56_verify_candidate_rows_and_combined_aggregate_counts_20260531_232628/date_range_aggregate/per_day_summary.csv
run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/date_range_aggregate/combined_candidate_audit.csv
run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/date_range_aggregate/combined_economics_summary.json
run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/date_range_aggregate/combined_family_side_summary.csv
run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/date_range_aggregate/per_day_summary.csv
run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/01_dataset_summary.json
run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/04_metrics_summary.json
run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/06_candidate_audit.csv
run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/artifacts/10_run_summary.json
run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/artifacts/11_run_summary.csv
run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/artifacts/economics_summary.json
run/replay/b3_r61d/B3-R61D_A7_NORMALIZED_TS_EVENT_SYMBOL_REPLAY_SMOKE_NO_REDIS_NO_PATCH_NO_ORDER_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337/replay_locked_single_day_b3-r61d_a7_normalized_ts_event_symbol_replay_smoke_no_redis_no_patch_no_order_rebuild_a7_dataset_with_ts_event_symbol_from_ts_event_ns_trading_symbol_then_run_replay_exports_audit_20260602_222337_20260602_165416_54b0e7b7/artifacts/execution_shadow_results.json

## Current R2C replay run summary for PnL precondition
R2C_PROOF=run/proofs/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738.json
R2C_RUN_DIR=run/replay/lane_b_r2c/LANE-B-R2C_EXACT_A7_20260602_OFFLINE_REPLAY_SMOKE_NO_PATCH_NO_ORDER_20260607_135738/replay_locked_single_day_lane-b-r2c_exact_a7_20260602_offline_replay_smoke_no_patch_no_order_20260607_135738_20260607_082750_2abac04b
replay_scope=feeds_features_strategy
candidate_count=0
trade_count=0
pnl_total=None
risk_row_count=0
execution_shadow_row_count=0
execution_shadow_filled_count=0
strategy_action_breakdown={'HOLD': 134035}
feature_side_breakdown={'CALL': 56400, 'CONTEXT': 21808, 'PUT': 55827}
feature_leg_breakdown={'CALL_ATM': 56400, 'FUTURES': 21808, 'PUT_ATM': 55827}

CLASSIFICATION=REVIEW_R3_RISK_EXECUTION_SHADOW_PNL_READINESS_SURFACES_INCOMPLETE
