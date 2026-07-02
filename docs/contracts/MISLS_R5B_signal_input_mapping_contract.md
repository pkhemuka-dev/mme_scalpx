{
  "canonical_input_layers_to_map": [
    "family_features.common.selected_option",
    "family_surfaces.surfaces_by_branch.<family>_<branch>.selected_features",
    "family_surfaces.surfaces_by_branch.<family>_<branch>.tradability",
    "shared_core.trap_events",
    "shared_core.miso_shadow_microstructure or shadow_features if present",
    "consumer_view.family_surfaces / branch_frames for strategy-side read-only future use"
  ],
  "classification": "MISLS_R5B_SIGNAL_INPUT_MAPPING_CONTRACT",
  "do_not_touch_yet": [
    "features.py runtime flow",
    "strategy.py runtime flow",
    "FAMILY_ORDER",
    "registry",
    "activation",
    "risk",
    "execution",
    "broker",
    "paper/live config",
    "Redis write/delete"
  ],
  "misls_required_signal_groups": [
    "recent range high/low or OR5/OR15 levels",
    "sweep beyond recent high/low",
    "fake breakout/breakdown failure",
    "reentry/reclaim/reject confirmation",
    "futures flow/velocity/imbalance confirmation",
    "selected option quote/tradability confirmation",
    "paired option quote validity"
  ],
  "preferred_next_step": "R5C write read-only input extractor contract/helper, still no wiring"
}