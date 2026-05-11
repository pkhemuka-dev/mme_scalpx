"""Replay optimization package for MME-ScalpX.

Lane D owns offline-only replay optimization contracts, sweep schemas,
leaderboard schemas, research-only profile generation, read-only replay/RAW
indexing, candidate-matrix construction, leaderboard construction, ML dataset
export contracts, result-binding schemas, sample/overfit risk reports,
implementation gates, replay result source maps, binding precondition audits,
grouped source-map repair contracts, grouped source-map precondition audits,
replay result-pack discovery audits, and result-pack verification audits.

It does not own replay execution, live services, broker IO, risk/execution
truth, strategy doctrine mutation, model training, paper/live enablement, or
Redis truth.
"""

from .contracts import *  # noqa: F401,F403
from .sweep_space import *  # noqa: F401,F403
from .profile_generator import *  # noqa: F401,F403
from .result_indexer import *  # noqa: F401,F403
from .raw_indexer import *  # noqa: F401,F403
from .candidate_matrix import *  # noqa: F401,F403
from .leaderboard import *  # noqa: F401,F403
from .ml_dataset import *  # noqa: F401,F403
from .result_binding import *  # noqa: F401,F403
from .sample_risk import *  # noqa: F401,F403
from .implementation_gate import *  # noqa: F401,F403
from .source_map import *  # noqa: F401,F403
from .precondition_audit import *  # noqa: F401,F403
from .source_map_grouping import *  # noqa: F401,F403
from .grouped_precondition_audit import *  # noqa: F401,F403
from .result_pack_discovery import *  # noqa: F401,F403
from .result_pack_verification import *  # noqa: F401,F403
from .row_count_normalization import *  # noqa: F401,F403
from .nonzero_pack_discovery import *  # noqa: F401,F403
from .nonzero_pack_verification import *  # noqa: F401,F403
from .candidate_trade_matching import *  # noqa: F401,F403
from .candidate_trade_readiness import *  # noqa: F401,F403
from .match_key_discovery import *  # noqa: F401,F403
from .matching_dry_run import *  # noqa: F401,F403
from .match_key_adapter import *  # noqa: F401,F403
from .candidate_context_enrichment import *  # noqa: F401,F403
from .context_source_discovery import *  # noqa: F401,F403
from .context_source_mapping import *  # noqa: F401,F403
from .context_enrichment_dry_run import *  # noqa: F401,F403
from .candidate_result_bridge import *  # noqa: F401,F403
from .candidate_context_value_source import *  # noqa: F401,F403
from .candidate_replay_binding_requirement import *  # noqa: F401,F403
from .candidate_replay_binding_plan import *  # noqa: F401,F403
from .candidate_replay_binding_plan_validator import *  # noqa: F401,F403
from .candidate_replay_materialization import *  # noqa: F401,F403
from .candidate_replay_materialization_validator import *  # noqa: F401,F403
from .candidate_replay_materialization_preflight import *  # noqa: F401,F403
from .lane_ce_handoff import *  # noqa: F401,F403
from .phase_gate_summary import *  # noqa: F401,F403
from .lane_ce_execution_package_requirement import *  # noqa: F401,F403
from .lane_d_freeze_summary import *  # noqa: F401,F403
from .lane_e_candidate_intake import *  # noqa: F401,F403

