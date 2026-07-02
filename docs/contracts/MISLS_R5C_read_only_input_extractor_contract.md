{
  "canonical_inputs": [
    "family_features.common.futures",
    "family_features.common.selected_option",
    "family_features.common.selected_option_rich",
    "family_surfaces.surfaces_by_branch.<source_family>_<branch>.selected_features",
    "family_surfaces.surfaces_by_branch.<source_family>_<branch>.tradability",
    "family_surfaces.surfaces_by_branch.<source_family>_<branch>.shadow_features",
    "shared_core.trap_events.<branch>",
    "shared_core.miso_shadow_microstructure.<branch>",
    "consumer_view.family_surfaces as future read-only fallback"
  ],
  "classification": "MISLS_R5C_READ_ONLY_INPUT_EXTRACTOR_CONTRACT",
  "forbidden": [
    "features.py runtime flow patch",
    "strategy.py runtime flow patch",
    "registry patch",
    "activation patch",
    "FAMILY_ORDER patch",
    "risk/execution/broker/paper/live/Redis writes"
  ],
  "new_module": "app/mme_scalpx/services/strategy_family/misls_input_extractor.py",
  "purpose": "Normalize existing in-memory family_features/family_surfaces/shared_core/consumer_view surfaces into MISLS read-only input snapshots.",
  "source_family_priority": [
    "MISO",
    "MISR",
    "MIST",
    "MISB",
    "MISC"
  ]
}