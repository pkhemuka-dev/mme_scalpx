# A6-FEED-R5AQ_read_only_extract_contracts_import_failure_after_ast_stage_flag_patch_pass_no_patch_no_restart_no_order_no_paper_20260515_152457 Contracts Import Failure Extraction

Batch: A6-FEED-R5AQ

Verdict: PASS_A6_FEED_R5AQ_CONTRACTS_IMPORT_FAILURE_EXTRACTED_NO_PATCH_NO_RESTART_NO_ORDER_NO_PAPER

Safety: read-only import failure extraction only; no patch, no restore, no service start/restart/stop, no Redis write, no paper/live, no broker/order, no risk/execution.

Classification:

```json
{
  "ast_surface": {
    "end_line": 250,
    "found": true,
    "line": 234,
    "required_keys_present": true,
    "target_count": 1,
    "values": [
      "data_valid",
      "data_quality_ok",
      "session_eligible",
      "warmup_complete",
      "tradability_ok",
      "risk_veto_active",
      "reconciliation_lock_active",
      "active_position_present",
      "provider_ready_classic",
      "provider_ready_miso",
      "dhan_context_fresh",
      "selected_option_present",
      "futures_present",
      "call_present",
      "put_present"
    ],
    "window": "    226:     \"call\",\n    227:     \"put\",\n    228:     \"selected_option\",\n    229:     \"cross_option\",\n    230:     \"economics\",\n    231:     \"signals\",\n    232: )\n    233: \n >> 234: STAGE_FLAG_KEYS: Final[tuple[str, ...]] = (\n    235:     \"data_valid\",\n    236:     \"data_quality_ok\",\n    237:     \"session_eligible\",\n    238:     \"warmup_complete\",\n    239:     \"tradability_ok\",\n    240:     \"risk_veto_active\",\n    241:     \"reconciliation_lock_active\",\n    242:     \"active_position_present\",\n    243:     \"provider_ready_classic\",\n    244:     \"provider_ready_miso\",\n    245:     \"dhan_context_fresh\",\n    246:     \"selected_option_present\",\n    247:     \"futures_present\",\n    248:     \"call_present\",\n    249:     \"put_present\",\n    250: )\n    251: \n    252: COMMON_FUTURES_KEYS: Final[tuple[str, ...]] = (\n    253:     \"ltp\",\n    254:     \"spread\",\n    255:     \"spread_ratio\",\n    256:     \"depth_total\",\n    257:     \"depth_ok\",\n    258:     \"top5_bid_qty\","
  },
  "decisions_stream_age_ms": 19912016,
  "decisions_stream_xlen": 1684,
  "features_stream_age_ms": 16627653,
  "features_stream_xlen": 131,
  "import_probe_summary": {
    "direct_ast_only": {
      "ok": true,
      "parsed": {
        "kind": "direct_ast_only",
        "ok": true,
        "required_keys_present": true,
        "stage_flag_keys": [
          "data_valid",
          "data_quality_ok",
          "session_eligible",
          "warmup_complete",
          "tradability_ok",
          "risk_veto_active",
          "reconciliation_lock_active",
          "active_position_present",
          "provider_ready_classic",
          "provider_ready_miso",
          "dhan_context_fresh",
          "selected_option_present",
          "futures_present",
          "call_present",
          "put_present"
        ],
        "tradability_ok_count": 1
      },
      "rc": 0,
      "stderr_tail": "",
      "stdout_tail": "{\"kind\": \"direct_ast_only\", \"ok\": true, \"required_keys_present\": true, \"stage_flag_keys\": [\"data_valid\", \"data_quality_ok\", \"session_eligible\", \"warmup_complete\", \"tradability_ok\", \"risk_veto_active\", \"reconciliation_lock_active\", \"active_position_present\", \"provider_ready_classic\", \"provider_ready_miso\", \"dhan_context_fresh\", \"selected_option_present\", \"futures_present\", \"call_present\", \"put_present\"], \"tradability_ok_count\": 1}"
    },
    "importlib_module": {
      "ok": false,
      "parsed": {
        "error": "stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'tradability_ok', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present')",
        "error_type": "FeatureFamilyContractError",
        "kind": "importlib_module",
        "ok": false
      },
      "rc": 1,
      "stderr_tail": "Traceback (most recent call last):\n  File \"<string>\", line 5, in <module>\n  File \"/usr/lib/python3.10/importlib/__init__.py\", line 126, in import_module\n    return _bootstrap._gcd_import(name[level:], package, level)\n  File \"<frozen importlib._bootstrap>\", line 1050, in _gcd_import\n  File \"<frozen importlib._bootstrap>\", line 1027, in _find_and_load\n  File \"<frozen importlib._bootstrap>\", line 992, in _find_and_load_unlocked\n  File \"<frozen importlib._bootstrap>\", line 241, in _call_with_frames_removed\n  File \"<frozen importlib._bootstrap>\", line 1050, in _gcd_import\n  File \"<frozen importlib._bootstrap>\", line 1027, in _find_and_load\n  File \"<frozen importlib._bootstrap>\", line 1006, in _find_and_load_unlocked\n  File \"<frozen importlib._bootstrap>\", line 688, in _load_unlocked\n  File \"<frozen importlib._bootstrap_external>\", line 883, in exec_module\n  File \"<frozen importlib._bootstrap>\", line 241, in _call_with_frames_removed\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/__init__.py\", line 40, in <module>\n    from . import common\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/common.py\", line 38, in <module>\n    from app.mme_scalpx.services.feature_family import contracts as C\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1740, in <module>\n    validate_family_features_payload(build_empty_family_features_payload())\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1607, in validate_family_features_payload\n    validate_stage_flags_block(\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1332, in validate_stage_flags_block\n    _require_exact_keys(\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 659, in _require_exact_keys\n    raise FeatureFamilyContractError(\napp.mme_scalpx.services.feature_family.contracts.FeatureFamilyContractError: stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'tradability_ok', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present')",
      "stdout_tail": "{\"error\": \"stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'tradability_ok', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present')\", \"error_type\": \"FeatureFamilyContractError\", \"kind\": \"importlib_module\", \"ok\": false}"
    },
    "package_attr": {
      "ok": false,
      "parsed": {
        "error": "stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'tradability_ok', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present')",
        "error_type": "FeatureFamilyContractError",
        "kind": "package_attr",
        "ok": false
      },
      "rc": 1,
      "stderr_tail": "Traceback (most recent call last):\n  File \"<string>\", line 5, in <module>\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/__init__.py\", line 40, in <module>\n    from . import common\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/common.py\", line 38, in <module>\n    from app.mme_scalpx.services.feature_family import contracts as C\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1740, in <module>\n    validate_family_features_payload(build_empty_family_features_payload())\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1607, in validate_family_features_payload\n    validate_stage_flags_block(\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1332, in validate_stage_flags_block\n    _require_exact_keys(\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 659, in _require_exact_keys\n    raise FeatureFamilyContractError(\napp.mme_scalpx.services.feature_family.contracts.FeatureFamilyContractError: stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'tradability_ok', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present')",
      "stdout_tail": "{\"error\": \"stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'tradability_ok', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present')\", \"error_type\": \"FeatureFamilyContractError\", \"kind\": \"package_attr\", \"ok\": false}"
    }
  },
  "likely_condition": "CONTRACTS_AST_OK_BUT_PACKAGE_IMPORT_FAILS",
  "next_action": "Inspect package import stderr/root cause read-only before any patch or restart.",
  "r5ao_final_verdict": "PASS_A6_FEED_R5AO_TRADABILITY_OK_ADDED_TO_STAGE_FLAG_KEYS_COMPILED_NO_RESTART_NO_ORDER_NO_PAPER",
  "r5ao_likely_condition": "STAGE_FLAG_KEYS_VALIDATOR_NOW_ACCEPTS_TRADABILITY_OK",
  "r5ao_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AO_approved_narrow_source_patch_add_tradability_ok_to_stage_flag_keys_no_start_no_restart_no_order_no_paper_20260515_152117.json",
  "r5ap_final_verdict": "FAIL_A6_FEED_R5AP_STATIC_IMPORT_VALIDATION_OR_SAFETY_CHECK",
  "r5ap_import_validation": {
    "command": [
      ".venv/bin/python",
      "-c",
      "\nfrom __future__ import annotations\nimport inspect, json\nfrom app.mme_scalpx.services.feature_family import contracts as c\n\nkeys = tuple(getattr(c, \"STAGE_FLAG_KEYS\", ()))\nresult = {\n    \"import_ok\": True,\n    \"stage_flag_keys\": list(keys),\n    \"has_tradability_ok\": \"tradability_ok\" in keys,\n    \"tradability_ok_count\": list(keys).count(\"tradability_ok\"),\n    \"required_keys_present\": set([\"data_valid\",\"data_quality_ok\",\"session_eligible\",\"warmup_complete\",\"tradability_ok\"]).issubset(set(keys)),\n    \"validator_call\": {\"attempted\": False, \"ok\": None, \"error\": None},\n}\n\nfn = getattr(c, \"validate_stage_flags_block\", None)\nif callable(fn):\n    result[\"validator_call\"][\"attempted\"] = True\n    flags = {k: False for k in keys}\n    attempts = []\n    for args, kwargs in [\n        ((flags,), {}),\n        ((flags, \"stage_flags\"), {}),\n        ((flags,), {\"path\": \"stage_flags\"}),\n    ]:\n        try:\n            ret = fn(*args, **kwargs)\n            attempts.append({\"ok\": True, \"return_type\": type(ret).__name__})\n            result[\"validator_call\"][\"ok\"] = True\n            break\n        except TypeError as e:\n            attempts.append({\"ok\": False, \"error\": \"TypeError: \" + str(e)})\n        except Exception as e:\n            attempts.append({\"ok\": False, \"error\": type(e).__name__ + \": \" + str(e)})\n    if result[\"validator_call\"][\"ok\"] is not True:\n        result[\"validator_call\"][\"ok\"] = False\n        result[\"validator_call\"][\"error\"] = attempts[-1][\"error\"] if attempts else \"no attempts\"\n    result[\"validator_call\"][\"attempts\"] = attempts\n\nprint(json.dumps(result, sort_keys=True))\n"
    ],
    "ok": false,
    "parsed": null,
    "rc": 1,
    "stderr": "Traceback (most recent call last):\n  File \"<string>\", line 4, in <module>\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/__init__.py\", line 40, in <module>\n    from . import common\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/common.py\", line 38, in <module>\n    from app.mme_scalpx.services.feature_family import contracts as C\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1740, in <module>\n    validate_family_features_payload(build_empty_family_features_payload())\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1607, in validate_family_features_payload\n    validate_stage_flags_block(\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1332, in validate_stage_flags_block\n    _require_exact_keys(\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 659, in _require_exact_keys\n    raise FeatureFamilyContractError(\napp.mme_scalpx.services.feature_family.contracts.FeatureFamilyContractError: stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'tradability_ok', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present')",
    "stdout": ""
  },
  "r5ap_likely_condition": "STATIC_IMPORT_VALIDATION_OR_SAFETY_CHECK_FAILED",
  "r5ap_path": "/home/Lenovo/scalpx/projects/mme_scalpx/run/proofs/A6-FEED-R5AP_read_only_static_import_contract_validation_after_stage_flag_keys_patch_no_restart_no_order_no_paper_20260515_152315.json",
  "services": [
    "feeds"
  ]
}
```

Import probes:

```json
{
  "direct_ast_only": {
    "kind": "direct_ast_only",
    "ok": true,
    "parsed": {
      "kind": "direct_ast_only",
      "ok": true,
      "required_keys_present": true,
      "stage_flag_keys": [
        "data_valid",
        "data_quality_ok",
        "session_eligible",
        "warmup_complete",
        "tradability_ok",
        "risk_veto_active",
        "reconciliation_lock_active",
        "active_position_present",
        "provider_ready_classic",
        "provider_ready_miso",
        "dhan_context_fresh",
        "selected_option_present",
        "futures_present",
        "call_present",
        "put_present"
      ],
      "tradability_ok_count": 1
    },
    "rc": 0,
    "stderr": "",
    "stdout": "{\"kind\": \"direct_ast_only\", \"ok\": true, \"required_keys_present\": true, \"stage_flag_keys\": [\"data_valid\", \"data_quality_ok\", \"session_eligible\", \"warmup_complete\", \"tradability_ok\", \"risk_veto_active\", \"reconciliation_lock_active\", \"active_position_present\", \"provider_ready_classic\", \"provider_ready_miso\", \"dhan_context_fresh\", \"selected_option_present\", \"futures_present\", \"call_present\", \"put_present\"], \"tradability_ok_count\": 1}"
  },
  "importlib_module": {
    "kind": "importlib_module",
    "ok": false,
    "parsed": {
      "error": "stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'tradability_ok', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present')",
      "error_type": "FeatureFamilyContractError",
      "kind": "importlib_module",
      "ok": false
    },
    "rc": 1,
    "stderr": "Traceback (most recent call last):\n  File \"<string>\", line 5, in <module>\n  File \"/usr/lib/python3.10/importlib/__init__.py\", line 126, in import_module\n    return _bootstrap._gcd_import(name[level:], package, level)\n  File \"<frozen importlib._bootstrap>\", line 1050, in _gcd_import\n  File \"<frozen importlib._bootstrap>\", line 1027, in _find_and_load\n  File \"<frozen importlib._bootstrap>\", line 992, in _find_and_load_unlocked\n  File \"<frozen importlib._bootstrap>\", line 241, in _call_with_frames_removed\n  File \"<frozen importlib._bootstrap>\", line 1050, in _gcd_import\n  File \"<frozen importlib._bootstrap>\", line 1027, in _find_and_load\n  File \"<frozen importlib._bootstrap>\", line 1006, in _find_and_load_unlocked\n  File \"<frozen importlib._bootstrap>\", line 688, in _load_unlocked\n  File \"<frozen importlib._bootstrap_external>\", line 883, in exec_module\n  File \"<frozen importlib._bootstrap>\", line 241, in _call_with_frames_removed\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/__init__.py\", line 40, in <module>\n    from . import common\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/common.py\", line 38, in <module>\n    from app.mme_scalpx.services.feature_family import contracts as C\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1740, in <module>\n    validate_family_features_payload(build_empty_family_features_payload())\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1607, in validate_family_features_payload\n    validate_stage_flags_block(\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1332, in validate_stage_flags_block\n    _require_exact_keys(\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 659, in _require_exact_keys\n    raise FeatureFamilyContractError(\napp.mme_scalpx.services.feature_family.contracts.FeatureFamilyContractError: stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'tradability_ok', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present')",
    "stdout": "{\"error\": \"stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'tradability_ok', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present')\", \"error_type\": \"FeatureFamilyContractError\", \"kind\": \"importlib_module\", \"ok\": false}"
  },
  "package_attr": {
    "kind": "package_attr",
    "ok": false,
    "parsed": {
      "error": "stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'tradability_ok', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present')",
      "error_type": "FeatureFamilyContractError",
      "kind": "package_attr",
      "ok": false
    },
    "rc": 1,
    "stderr": "Traceback (most recent call last):\n  File \"<string>\", line 5, in <module>\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/__init__.py\", line 40, in <module>\n    from . import common\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/common.py\", line 38, in <module>\n    from app.mme_scalpx.services.feature_family import contracts as C\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1740, in <module>\n    validate_family_features_payload(build_empty_family_features_payload())\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1607, in validate_family_features_payload\n    validate_stage_flags_block(\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 1332, in validate_stage_flags_block\n    _require_exact_keys(\n  File \"/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/services/feature_family/contracts.py\", line 659, in _require_exact_keys\n    raise FeatureFamilyContractError(\napp.mme_scalpx.services.feature_family.contracts.FeatureFamilyContractError: stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'tradability_ok', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present')",
    "stdout": "{\"error\": \"stage_flags keys mismatch. expected=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'tradability_ok', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present') actual=('data_valid', 'data_quality_ok', 'session_eligible', 'warmup_complete', 'risk_veto_active', 'reconciliation_lock_active', 'active_position_present', 'provider_ready_classic', 'provider_ready_miso', 'dhan_context_fresh', 'selected_option_present', 'futures_present', 'call_present', 'put_present')\", \"error_type\": \"FeatureFamilyContractError\", \"kind\": \"package_attr\", \"ok\": false}"
  }
}
```

Required checks:

```json
{
  "all_feature_family_sources_compile": true,
  "all_watched_sources_compile": true,
  "ast_stage_flag_keys_found": true,
  "ast_stage_flag_keys_has_tradability_once": true,
  "ast_stage_flag_required_keys_present": true,
  "direct_ast_probe_ok": true,
  "latest_r5ao_pass_found": true,
  "latest_r5ap_failure_found": true,
  "no_broker_order": true,
  "no_lock_clear_delete": true,
  "no_paper_live": true,
  "no_patch": true,
  "no_redis_write": true,
  "no_restore": true,
  "no_risk_execution_order_process_visible": true,
  "no_service_start_restart_stop": true,
  "orders_mme_stream_zero_or_absent": true,
  "position_flat": true,
  "watched_sources_unchanged_by_this_batch": true
}
```

Failures:

```json
[]
```

Next rule:
- If package import fails but AST is OK, inspect import stderr/export path before any patch.
- No service restart until separate explicit approval.
- A6-PAPER remains blocked.
