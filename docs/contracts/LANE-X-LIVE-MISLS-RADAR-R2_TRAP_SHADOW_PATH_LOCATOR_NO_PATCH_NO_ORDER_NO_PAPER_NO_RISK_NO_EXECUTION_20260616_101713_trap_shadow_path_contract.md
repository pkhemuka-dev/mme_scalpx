{
  "classification": "PASS_LIVE_MISLS_R2_TRAP_SHADOW_PATH_LOCATOR_WRITTEN_NO_ORDER",
  "forbidden": [
    "paper order",
    "live order",
    "risk start",
    "execution start",
    "Redis delete",
    "lock delete",
    "features.py runtime patch",
    "strategy.py runtime patch",
    "FAMILY_ORDER/registry/activation patch"
  ],
  "interpretation": "This does not trade. It only proves whether true liquidity-sweep context is available in current feature payloads.",
  "outputs": {
    "paths_file": "run/audits/LANE-X-LIVE-MISLS-RADAR-R2_TRAP_SHADOW_PATH_LOCATOR_NO_PATCH_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_101713_trap_shadow_paths.json",
    "raw_sample": "run/audits/LANE-X-LIVE-MISLS-RADAR-R2_TRAP_SHADOW_PATH_LOCATOR_NO_PATCH_NO_ORDER_NO_PAPER_NO_RISK_NO_EXECUTION_20260616_101713_raw_tail_payloads.json"
  },
  "purpose": "Live no-patch locator for MISLS trap/shadow/microstructure paths."
}