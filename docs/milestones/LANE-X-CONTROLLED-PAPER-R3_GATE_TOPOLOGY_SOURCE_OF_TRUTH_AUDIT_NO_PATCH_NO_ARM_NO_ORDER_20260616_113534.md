# LANE-X-CONTROLLED-PAPER-R3_GATE_TOPOLOGY_SOURCE_OF_TRUTH_AUDIT_NO_PATCH_NO_ARM_NO_ORDER_20260616_113534

## Proof

```json
{
  "aliases_file": "run/audits/LANE-X-CONTROLLED-PAPER-R3_GATE_TOPOLOGY_SOURCE_OF_TRUTH_AUDIT_NO_PATCH_NO_ARM_NO_ORDER_20260616_113534_aliases_and_functions.txt",
  "base_live_visible": true,
  "classification": "REVIEW_CONTROLLED_PAPER_R3_STATE_KEYS_NOT_PUBLISHED_IN_RUNTIME_NO_ARM_NO_ORDER",
  "danger_env_absent": true,
  "helper_status": {
    "paper_status_found": false,
    "pstatus_found": false
  },
  "next_step": "If state key contract exists but runtime keys are absent, next step is after-market patch/harness to restore paper gate status publication. Do not arm paper from this audit.",
  "no_execution_start": true,
  "no_order": true,
  "no_paper_armed": true,
  "no_redis_delete": true,
  "no_risk_start": true,
  "no_source_patch": true,
  "observe_env_ok": true,
  "process_present": true,
  "python_constants": "run/audits/LANE-X-CONTROLLED-PAPER-R3_GATE_TOPOLOGY_SOURCE_OF_TRUTH_AUDIT_NO_PATCH_NO_ARM_NO_ORDER_20260616_113534_python_constants_scan.txt",
  "redis_file": "run/audits/LANE-X-CONTROLLED-PAPER-R3_GATE_TOPOLOGY_SOURCE_OF_TRUTH_AUDIT_NO_PATCH_NO_ARM_NO_ORDER_20260616_113534_redis_current_state.json",
  "redis_has_execution": true,
  "redis_has_paper_gate": false,
  "redis_has_position": false,
  "redis_has_risk": false,
  "source_grep": "run/audits/LANE-X-CONTROLLED-PAPER-R3_GATE_TOPOLOGY_SOURCE_OF_TRUTH_AUDIT_NO_PATCH_NO_ARM_NO_ORDER_20260616_113534_source_grep.txt",
  "source_has_controlled_paper": true,
  "source_has_execution_key": true,
  "source_has_position_key": true,
  "source_has_risk_key": true,
  "source_has_route_allowed": true,
  "tag": "LANE-X-CONTROLLED-PAPER-R3_GATE_TOPOLOGY_SOURCE_OF_TRUTH_AUDIT_NO_PATCH_NO_ARM_NO_ORDER_20260616_113534",
  "topology": "run/audits/LANE-X-CONTROLLED-PAPER-R3_GATE_TOPOLOGY_SOURCE_OF_TRUTH_AUDIT_NO_PATCH_NO_ARM_NO_ORDER_20260616_113534_gate_topology.json"
}
```

## Topology file

run/audits/LANE-X-CONTROLLED-PAPER-R3_GATE_TOPOLOGY_SOURCE_OF_TRUTH_AUDIT_NO_PATCH_NO_ARM_NO_ORDER_20260616_113534_gate_topology.json

## Source grep excerpt

```text
===== source grep: controlled paper / state / route / helpers =====
app/mme_scalpx/core/models.py:2513:    has_position: bool
app/mme_scalpx/core/models.py:2514:    position_side: str
app/mme_scalpx/core/models.py:2538:        _require_bool(self.has_position, "has_position")
app/mme_scalpx/core/models.py:2539:        _require_literal(self.position_side, "position_side", allowed=ALLOWED_POSITION_SIDES)
app/mme_scalpx/core/models.py:2573:        if self.has_position:
app/mme_scalpx/core/models.py:2575:                self.position_side in (
app/mme_scalpx/core/models.py:2586:            _require(self.position_side == names.POSITION_SIDE_FLAT, "flat position must use position_side FLAT")
app/mme_scalpx/core/models.py:2671:    veto_entries: bool
app/mme_scalpx/core/models.py:2688:        _require_bool(self.veto_entries, "veto_entries")
app/mme_scalpx/core/models.py:2883:    position_side: str | None = None
app/mme_scalpx/core/models.py:2908:        if self.position_side is not None:
app/mme_scalpx/core/models.py:2909:            _require_literal(self.position_side, "position_side", allowed=ALLOWED_POSITION_SIDES)
app/mme_scalpx/core/names.py:782:HASH_STATE_RISK: Final[str] = "state:risk"
app/mme_scalpx/core/names.py:783:HASH_STATE_POSITION_MME: Final[str] = "state:position:mme"
app/mme_scalpx/core/names.py:784:HASH_STATE_EXECUTION: Final[str] = "state:execution"
app/mme_scalpx/research_capture/models.py:659:    position_side: str | None = None
app/mme_scalpx/research_capture/contracts.py:662:        ("position_side", "str", SA, OPT, LIVE, AUD, (AP,), "Position side", ()),
app/mme_scalpx/main.py:127:        and not os.environ.get("SCALPX_PAPER_ARMED")
app/mme_scalpx/main.py:128:        and not os.environ.get("SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME")
app/mme_scalpx/main.py:1131:        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
app/mme_scalpx/main.py:1132:        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
app/mme_scalpx/main.py:1133:        "SCALPX_PAPER_ARMED",
app/mme_scalpx/main.py:1134:        "SCALPX_ENABLE_PAPER",
app/mme_scalpx/integrations/bootstrap_quote.py:78:        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
app/mme_scalpx/integrations/bootstrap_quote.py:79:        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
app/mme_scalpx/integrations/provider_runtime.py:846:    if inputs.position_state is not None and inputs.position_state.has_position:
app/mme_scalpx/integrations/provider_runtime.py:873:    has_open_position = bool(inputs.position_state.has_position) if inputs.position_state else False
app/mme_scalpx/integrations/broker_api.py:1437:_A6_R3_ALLOWED_CONTROLLED_PAPER_ROUTES = frozenset(("paper", "sandbox"))
app/mme_scalpx/integrations/broker_api.py:1492:def submit_controlled_paper_sandbox_order(
app/mme_scalpx/integrations/broker_api.py:1511:        "controlled_paper": True,
app/mme_scalpx/integrations/broker_api.py:1540:    if route not in _A6_R3_ALLOWED_CONTROLLED_PAPER_ROUTES:
app/mme_scalpx/integrations/broker_api.py:1543:            status="FAIL_CLOSED_INVALID_CONTROLLED_PAPER_ROUTE",
app/mme_scalpx/ops_dashboard/server.py:44:    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
app/mme_scalpx/ops_dashboard/server.py:45:    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
app/mme_scalpx/ops_dashboard/server.py:49:    "SCALPX_PAPER_ARMED",
app/mme_scalpx/ops_dashboard/server.py:50:    "SCALPX_ENABLE_PAPER",
app/mme_scalpx/ops_dashboard/server.py:53:    "MME_ENABLE_PAPER",
app/mme_scalpx/ops_dashboard/server.py:536:        "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME",
app/mme_scalpx/ops_dashboard/server.py:537:        "SCALPX_CONTROLLED_PAPER_SCOPE_ACK",
app/mme_scalpx/ops_dashboard/server.py:541:        "SCALPX_PAPER_ARMED",
app/mme_scalpx/ops_dashboard/server.py:542:        "SCALPX_ENABLE_PAPER",
app/mme_scalpx/ops/healthcheck.py:226:        side = _first_present(payload, ("side", "position_side", "state"))
app/mme_scalpx/ops/healthcheck.py:230:        veto = _first_present(payload, ("veto_entries", "entries_vetoed", "block_entries"))
app/mme_scalpx/ops/healthcheck.py:232:            summary_parts.append(f"veto_entries={veto}")
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:172:        from app.mme_scalpx.services.controlled_paper_runtime import (
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:393:    veto_entries: bool
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:557:            "pending_order_json": "",
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:569:            "has_position": 0,
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:570:            "position_side": N.POSITION_SIDE_FLAT,
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:605:        state["pending_order_json"] = _safe_str(raw.get("pending_order_json"))
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:632:        state["has_position"] = 1 if _safe_bool(raw.get("has_position")) else 0
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:633:        state["position_side"] = _safe_str(
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:634:            raw.get("position_side") or raw.get("side"),
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:856:            pending_json = _safe_str(self.execution_state.get("pending_order_json"))
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:997:        self.execution_state["pending_order_json"] = ""
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1029:        if not _safe_bool(broker_state.get("has_position"), False):
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1035:        self.position_state["has_position"] = 1
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1036:        self.position_state["position_side"] = _safe_str(
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1037:            broker_state.get("position_side") or broker_state.get("side"),
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1091:            self.execution_state["pending_order_json"] = ""
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1118:            self.execution_state["pending_order_json"] = ""
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1149:        self.execution_state["pending_order_json"] = _json_dumps(
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1247:        if _safe_bool(self.position_state.get("has_position"), False):
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1258:        if risk_gate.veto_entries:
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1333:        self.execution_state["pending_order_json"] = _json_dumps(
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1357:        if not _safe_bool(self.position_state.get("has_position"), False):
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1432:        self.execution_state["pending_order_json"] = _json_dumps(
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1469:        self.execution_state["pending_order_json"] = _json_dumps(
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1492:            self.execution_state["pending_order_json"] = ""
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1530:        self.position_state["has_position"] = 1
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1531:        self.position_state["position_side"] = side
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1548:        self.execution_state["pending_order_json"] = ""
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1564:            position_side=side,
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1594:        prior_position_side = _safe_str(
app/mme_scalpx/services/execution.py.r38x_backup_20260615_131026:1595:            self.position_state.get("position_side"),

```
