# LANE-X-R36H_DASHBOARD_ONLY_PSTATUS_VISIBILITY_RESEAL_NO_MME_START_NO_ORDER_NO_PAPER_20260614_110800

classification: PASS_LANE_X_R36H_DASHBOARD_ONLY_PSTATUS_VISIBILITY_RESEALED_NO_MME_START_NO_ORDER_NO_PAPER
proof: `run/proofs/LANE-X-R36H_DASHBOARD_ONLY_PSTATUS_VISIBILITY_RESEAL_NO_MME_START_NO_ORDER_NO_PAPER_20260614_110800.json`
dashboard_url: `http://127.0.0.1:8765/`
dashboard_log: `run/ops_dashboard_r36h_20260614_110800.log`

dashboard_pid_before=2147
dashboard_pid_after=2147
dashboard_start_rc=0
compile_rc=0 curl_rc=0 page_marker_rc=0
pstatus_pre_rc=0 pstatus_post_rc=0
paper_route_allowed=false
pstatus_reason=OBSERVE_ONLY_ACTIVE
safety pre=0/0/0 post=0/0/0
proc pre=0/0 replay=0 post=0/0 replay=0

## Interpretation
- Dashboard was started/reused only as dashboard visibility.
- MME stack was not started.
- Risk/execution were not started.
- Paper/live remains blocked by pstatus.

## Source visibility audit
## dashboard_source_markers
19:VERSION = "OPS-DASH-R4B-LX-R3E-REPLAY-SKELETON"
387:            "<tr><td>Paper status</td><td class='mono'>PAPER BLOCKED - dashboard never promotes paper</td></tr>"
521:            "<tr><td>Paper status</td><td class='mono'>PAPER BLOCKED - requires sealed day + candidate/shadow proof + approval</td></tr>"
600:        + " | PAPER BLOCKED"
606:        ("Paper status", "PAPER BLOCKED - needs capture-grade + candidate/shadow proof + explicit approval"),
677:# LANE_X_DASH_R4B_INTEGRATED_REPLAY_BACKTEST_UI_SKELETON
678:# LANE_X_DASH_R4B_R2_PNL_LABEL_MARKER_HARDEN
953:        "<tr><td>Mode</td><td class='mono'>R4B_UI_ONLY_SKELETON</td></tr>"
967:        "<div class='panel' id='replay-backtest'><h2>Replay / Backtest</h2>"
978:        + "<h3>R4B Output Tables Planned</h3>"
1086:<title>MME-ScalpX OPS Dashboard R3H-LX-R3E</title>
1110:<div><h1>MME-ScalpX OPS Dashboard R3H-LX-R3E</h1><div class="sub">R3H-LX-R3E read-only · HOLD reason capped · action distribution · capture progress · paper blocked · no writes · no orders</div></div>

## source sha256
7d81bed8962735c18c86322820362d4b8df465523acadf89258713fbaa329770  app/mme_scalpx/ops_dashboard/server.py
6f30000b8336b32704ce2a9293c6efe058dbb331faecc1ae8a8a19f5c7a86a98  bin/pstatus
1b10dd87931a957defbb75abeca7a761ca7bac227903e2230b49ec852d7015e6  docs/runbooks/CONTROLLED_PAPER_SOURCE_OF_TRUTH.md

## Dashboard page markers
7:<title>MME-ScalpX OPS Dashboard R3H-LX-R3E</title>
31:<div><h1>MME-ScalpX OPS Dashboard R3H-LX-R3E</h1><div class="sub">R3H-LX-R3E read-only · HOLD reason capped · action distribution · capture progress · paper blocked · no writes · no orders</div></div>
46:<div class='panel' id='replay-backtest'><h2>Replay / Backtest</h2><p class='mono'>Historical what-would-have-happened view only. This section never changes the Live Truth Board or paper/live readiness.</p><form method='get' action='/' class='mono'><table><tr><td>Date from</td><td><input name='date_from' value='' placeholder='YYYY-MM-DD'></td><td>Date to</td><td><input name='date_to' value='' placeholder='YYYY-MM-DD'></td></tr><tr><td>Date mode</td><td><select name='date_mode'><option value='single_day' selected>single_day</option><option value='date_range'>date_range</option></select></td><td>Strategy</td><td><select name='strategy'><option value='all' selected>all</option><option value='MIST'>MIST</option><option value='MISB'>MISB</option><option value='MISC'>MISC</option><option value='MISR'>MISR</option><option value='MISO'>MISO</option><option value='MIV-R'>MIV-R</option></select></td></tr><tr><td>Side</td><td><select name='side'><option value='all' selected>all</option><option value='CALL'>CALL</option><option value='PUT'>PUT</option></select></td><td>Report type</td><td><select name='report_type'><option value='candidate_summary' selected>candidate_summary</option><option value='trade_candidates'>trade_candidates</option><option value='near_candidates'>near_candidates</option><option value='shadow_fills'>shadow_fills</option><option value='pnl'>pnl</option><option value='strategy_wise_pnl'>strategy_wise_pnl</option><option value='day_wise_pnl'>day_wise_pnl</option><option value='blocker_summary'>blocker_summary</option><option value='failed_stage_summary'>failed_stage_summary</option><option value='score_distribution'>score_distribution</option><option value='full_replay_report'>full_replay_report</option></select></td></tr><tr><td>Dataset source</td><td><select name='dataset_source'><option value='latest_available' selected>latest_available</option><option value='sealed_live_capture'>sealed_live_capture</option><option value='replay_dataset'>replay_dataset</option><option value='evidence_bundle'>evidence_bundle</option></select></td><td>Action</td><td><button type='submit'>Apply display filter</button></td></tr></table></form><h3>Selected Replay View</h3><table><tr><td>Mode</td><td class='mono'>R4B_UI_ONLY_SKELETON</td></tr><tr><td>Selected filter</td><td class='mono'>date_from= date_to= date_mode=single_day strategy=all side=all report_type=candidate_summary dataset_source=latest_available</td></tr><tr><td>Safety</td><td class='mono'>READ_ONLY_FILES_ONLY | NO_REPLAY_EXECUTION | NO_SHELL_COMMAND | NO_LIVE_STATE_MUTATION</td></tr><tr><td>UI caps</td><td class='mono'>runs=20 files=50 rows=500</td></tr><tr><td>Source hierarchy</td><td class='mono'>proof/report JSON/MD → 10_run_summary.json → engine_result.json → capped summaries → raw datasets only by later explicit action</td></tr><tr><td>MIV-R label</td><td class='mono'>MIV-R = research/audit probe only, not production strategy, not paper/live candidate source</td></tr></table><h3>Synthetic Shadow PnL</h3><p class='mono'>Replay-only synthetic shadow model. not broker PnL, not paper PnL, not live PnL. PNL_COMPUTED_REPLAY_ONLY_SYNTHETIC_SHADOW_MODEL_NOT_BROKER_NOT_PAPER_NOT_LIVE. Keep separate from Official closed-trade PnL, Broker/Paper/Live PnL, and Live Truth Board.</p><table><tr><th>Time</th><th>Artifact</th><th>Summary</th></tr><tr><td class='mono'>2026-06-14T00:38:43</td><td class='mono'>run/proofs/R35C_R5D_JUNE01_VERIFY_SUMMARY_SYNTHETIC_PNL_AGGREGATION_NO_ORDER_20260614_003605.json</td><td class='mono'>big_files_over_50mb=0 | classification=PASS_R35C_R5D_JUNE01_SUMMARY_SYNTHETIC_PNL_AGGREGATION_VERIFIED_NO_ORDER | pnl_total=21110.0 | replay_proc=0 | replay_rc=0 | safety_post=0/0/0 | shadow_pnl_total=21110.0 | trade_count=4222 | win_count=4222</td></tr></table><h3>Latest Replay Runs</h3><table><tr><th>Modified</th><th>Run path</th><th>Summary artifacts</th></tr><tr><td class='mono'>2026-06-14T00:36:05</td><td class='mono'>run/replay/r35c_r5d</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-14T00:26:35</td><td class='mono'>run/replay/r35c_r5b</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-14T00:03:14</td><td class='mono'>run/replay/r35c_r4x</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T23:34:14</td><td class='mono'>run/replay/r35c_r4t</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T23:14:19</td><td class='mono'>run/replay/r35c_r4s</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T23:07:35</td><td class='mono'>run/replay/r35c_r4q</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T22:43:14</td><td class='mono'>run/replay/r35c_r4m</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T22:37:10</td><td class='mono'>run/replay/r35c_r4k</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T22:28:43</td><td class='mono'>run/replay/r35c_r4h</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T22:26:16</td><td class='mono'>run/replay/r35c_r4g</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T22:22:14</td><td class='mono'>run/replay/r35c_r4f</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T22:14:14</td><td class='mono'>run/replay/r35c_r4d</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T22:01:30</td><td class='mono'>run/replay/r35c_r4a</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T19:30:46</td><td class='mono'>run/replay/staging</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T19:16:56</td><td class='mono'>run/replay/r35b_r4t</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T18:14:31</td><td class='mono'>run/replay/r35b_r4j</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T18:08:21</td><td class='mono'>run/replay/r35b_r4h</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T17:54:55</td><td class='mono'>run/replay/r35b_r4f</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T17:40:35</td><td class='mono'>run/replay/r35b_r4c</td><td class='mono'>-</td></tr><tr><td class='mono'>2026-06-13T17:32:42</td><td class='mono'>run/replay/r35b_r4b</td><td class='mono'>-</td></tr></table><h3>Latest Existing Replay / PnL / Candidate Reports</h3><table><tr><th>Modified</th><th>Size</th><th>Path</th></tr><tr><td class='mono'>2026-06-14T11:07:42</td><td class='mono'>0.001 MB</td><td class='mono'>run/audits/LANE-X-DASH-R4C-DIAG_NO_PATCH_RUNTIME_EXCEPTION_DIAGNOSIS_NO_REPLAY_EXEC_NO_ORDER_NO_PAPER_diagnose_r4c_r2_page_marker_failure_without_patch_or_replay_20260614_110740_report.md</td></tr><tr><td class='mono'>2026-06-14T11:05:29</td><td class='mono'>0.002 MB</td><td class='mono'>run/audits/LANE-X-DASH-R4C-R2-R1_RECOVER_STABLE_R4B_R2_AND_CAPTURE_R4C_R2_FAILURE_NO_REPLAY_EXEC_NO_ORDER_NO_PAPER_rollback_from_failed_r4c_r2_to_stable_r4b_r2_20260614_110522_report.md</td></tr><tr><td class='mono'>2026-06-14T10:59:13</td><td class='mono'>0.001 MB</td><td class='mono'>run/audits/LANE-X-DASH-R4C-R1B_RECOVER_STABLE_R4B_R2_FROM_CORRECT_BACKUP_NO_REPLAY_EXEC_NO_ORDER_NO_PAPER_recover_dashboard_from_real_r4c_or_r4b_r2_backup_20260614_105906_report.md</td></tr><tr><td class='mono'>2026-06-14T10:56:31</td><td class='mono'>0.000 MB</td><td class='mono'>run/audits/LANE-X-DASH-R4C-R1_RECOVER_STABLE_R4B_R2_DASHBOARD_AND_CAPTURE_R4C_FAILURE_NO_REPLAY_EXEC_NO_ORDER_NO_PAPER_rollback_dashboard_to_last_stable_r4b_r2_and_preserve_r4c_failure_evidence_20260614_105630_report.md</td></tr><tr><td class='mono'>2026-06-14T00:59:37</td><td class='mono'>0.004 MB</td><td class='mono'>run/proofs/LANE-X-DASH-R4C_READ_ONLY_REPLAY_SUMMARY_RENDERER_FROM_EXISTING_ARTIFACTS_NO_REPLAY_EXEC_NO_ORDER_NO_PAPER_patch_dashboard_to_render_existing_replay_summary_artifacts_read_only_20260614_005928.json</td></tr><tr><td class='mono'>2026-06-14T00:59:37</td><td class='mono'>0.002 MB</td><td class='mono'>run/audits/LANE-X-DASH-R4C_READ_ONLY_REPLAY_SUMMARY_RENDERER_FROM_EXISTING_ARTIFACTS_NO_REPLAY_EXEC_NO_ORDER_NO_PAPER_patch_dashboard_to_render_existing_replay_summary_artifacts_read_only_20260614_005928_report.md</td></tr><tr><td class='mono'>2026-06-14T00:57:45</td><td class='mono'>0.002 MB</td><td class='mono'>run/audits/LANE-X-DASH-R4B-R2_PNL_LABEL_MARKER_HARDEN_RUNTIME_SEAL_DASHBOARD_ONLY_NO_REPLAY_EXEC_NO_ORDER_NO_PAPER_harden_exact_replay_pnl_not_broker_not_paper_not_live_labels_20260614_005738_report.md</td></tr><tr><td class='mono'>2026-06-14T00:56:20</td><td class='mono'>0.002 MB</td><td class='mono'>run/audits/LANE-X-DASH-R4B-R2_PNL_LABEL_MARKER_HARDEN_RUNTIME_SEAL_DASHBOARD_ONLY_NO_REPLAY_EXEC_NO_ORDER_NO_PAPER_harden_exact_replay_pnl_not_broker_not_paper_not_live_labels_20260614_005613_report.md</td></tr><tr><td class='mono'>2026-06-14T00:39:02</td><td class='mono'>0.005 MB</td><td class='mono'>run/audits/LANE-X-DASH-R4A_INTEGRATED_REPLAY_DASHBOARD_SOURCE_AUDIT_AND_DESIGN_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_source_and_replay_backtest_scripts_then_design_integrated_replay_dashboard_section_20260614_003858_report.md</td></tr><tr><td class='mono'>2026-06-14T00:39:02</td><td class='mono'>0.161 MB</td><td class='mono'>run/audits/LANE-X-DASH-R4A_INTEGRATED_REPLAY_DASHBOARD_SOURCE_AUDIT_AND_DESIGN_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_source_and_replay_backtest_scripts_then_design_integrated_replay_dashboard_section_20260614_003858_replay_data_inventory.txt</td></tr><tr><td class='mono'>2026-06-14T00:38:58</td><td class='mono'>0.020 MB</td><td class='mono'>run/audits/LANE-X-DASH-R4A_INTEGRATED_REPLAY_DASHBOARD_SOURCE_AUDIT_AND_DESIGN_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_source_and_replay_backtest_scripts_then_design_integrated_replay_dashboard_section_20260614_003858_replay_source_inventory.txt</td></tr><tr><td class='mono'>2026-06-14T00:38:58</td><td class='mono'>0.005 MB</td><td class='mono'>run/audits/LANE-X-DASH-R4A_INTEGRATED_REPLAY_DASHBOARD_SOURCE_AUDIT_AND_DESIGN_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_source_and_replay_backtest_scripts_then_design_integrated_replay_dashboard_section_20260614_003858_dashboard_source_audit.txt</td></tr><tr><td class='mono'>2026-06-14T00:38:58</td><td class='mono'>0.001 MB</td><td class='mono'>run/audits/LANE-X-DASH-R4A_INTEGRATED_REPLAY_DASHBOARD_SOURCE_AUDIT_AND_DESIGN_NO_PATCH_NO_START_NO_ORDER_NO_PAPER_audit_existing_dashboard_source_and_replay_backtest_scripts_then_design_integrated_replay_dashboard_section_20260614_003858_safety_snapshot.txt</td></tr><tr><td class='mono'>2026-06-14T00:38:43</td><td class='mono'>0.001 MB</td><td class='mono'>run/proofs/R35C_R5D_JUNE01_VERIFY_SUMMARY_SYNTHETIC_PNL_AGGREGATION_NO_ORDER_20260614_003605.json</td></tr><tr><td class='mono'>2026-06-14T00:34:29</td><td class='mono'>0.005 MB</td><td class='mono'>run/audits/R35C_R5C_SUMMARY_SYNTHETIC_PNL_AGGREGATION_PATCH_NO_REPLAY_NO_ORDER_20260614_003429_report.md</td></tr><tr><td class='mono'>2026-06-14T00:34:29</td><td class='mono'>0.001 MB</td><td class='mono'>run/proofs/R35C_R5C_SUMMARY_SYNTHETIC_PNL_AGGREGATION_PATCH_NO_REPLAY_NO_ORDER_20260614_003429.json</td></tr><tr><td class='mono'>2026-06-14T00:29:22</td><td class='mono'>0.011 MB</td><td class='mono'>run/audits/R35C_R5B_JUNE01_VERIFY_EXECUTION_SHADOW_PNL_FIELDS_NO_ORDER_20260614_002635_report.md</td></tr><tr><td class='mono'>2026-06-14T00:23:40</td><td class='mono'>0.007 MB</td><td class='mono'>run/audits/R35C_R5A3_EXECUTION_SHADOW_PNL_FIELDS_BLOCK_REWRITE_NO_REPLAY_NO_ORDER_20260614_002340_report.md</td></tr><tr><td class='mono'>2026-06-14T00:20:22</td><td class='mono'>0.005 MB</td><td class='mono'>run/audits/R35C_R5A2_EXECUTION_SHADOW_PNL_FIELDS_LINE_PATCH_NO_REPLAY_NO_ORDER_20260614_002022_report.md</td></tr><tr><td class='mono'>2026-06-14T00:20:22</td><td class='mono'>0.001 MB</td><td class='mono'>run/proofs/R35C_R5A2_EXECUTION_SHADOW_PNL_FIELDS_LINE_PATCH_NO_REPLAY_NO_ORDER_20260614_002022.json</td></tr></table><h3>R4B Output Tables Planned</h3><p class='mono'>strategy_candidate_summary | trade_candidate_table | near_candidate_table | shadow_fill_table | pnl_summary | strategy_wise_pnl | day_wise_pnl | blocker_summary | failed_stage_summary | score_distribution | latest_exports</p></div>
47:<div class="panel"><h3>A7 Mission State</h3><table><tr><td>Mission</td><td class='mono'>SAFE | OBSERVE-ONLY NOT RUNNING | CAPTURE DATA NOT READY | DECISIONS PRESENT | NEW ERRORS TOTAL=10006 | PAPER BLOCKED</td></tr><tr><td>High-level state</td><td class='mono'>OBSERVE_ONLY_NOT_RUNNING</td></tr><tr><td>Paper status</td><td class='mono'>PAPER BLOCKED - needs capture-grade + candidate/shadow proof + explicit approval</td></tr><tr><td>Safety</td><td class='mono'>SAFE</td></tr><tr><td>Processes</td><td class='mono'>feeds=0 features=0 strategy=0 risk=0 execution=0</td></tr><tr><td>Streams</td><td class='mono'>fut_z=0 opt_z=0 features=4220 decisions=1682 errors=10006 orders=0 risk=0 execution=0</td></tr><tr><td>Risky env flags</td><td class='mono'>NONE</td></tr><tr><td>A7 interpretation</td><td class='mono'>capture/readiness visibility only - dashboard must not control live/paper services</td></tr></table></div>
48:<div class="panel"><h3>Capture-Grade Progress</h3><table><tr><td>Visible stream span</td><td class='mono'>27.8 min</td></tr><tr><td>Capture progress band</td><td class='mono'>DIAGNOSTIC_CAPTURE_10_TO_30_MIN</td></tr><tr><td>Paper status</td><td class='mono'>PAPER BLOCKED - requires sealed day + candidate/shadow proof + approval</td></tr><tr><td>B3 handoff</td><td class='mono'>B3 NEEDS CLEAN SEALED DAY</td></tr></table><table><tr><th>Label</th><th>Count</th><th>First ID</th><th>Latest ID</th><th>Span min</th><th>Rate</th></tr><tr><td>fut zerodha</td><td class='mono'>0</td><td class='mono'>-</td><td class='mono'>-</td><td class='mono'>0.0</td><td class='mono'>0.0/min</td></tr><tr><td>opt zerodha</td><td class='mono'>0</td><td class='mono'>-</td><td class='mono'>-</td><td class='mono'>0.0</td><td class='mono'>0.0/min</td></tr><tr><td>features</td><td class='mono'>4220</td><td class='mono'>1777886808402-0</td><td class='mono'>1777888201390-0</td><td class='mono'>23.2</td><td class='mono'>181.8/min</td></tr><tr><td>decisions</td><td class='mono'>1682</td><td class='mono'>1777887626443-0</td><td class='mono'>1777888475610-0</td><td class='mono'>14.2</td><td class='mono'>118.8/min</td></tr><tr><td>errors</td><td class='mono'>10006</td><td class='mono'>1777886937006-0</td><td class='mono'>1777888475661-0</td><td class='mono'>25.6</td><td class='mono'>390.2/min</td></tr><tr><td>orders</td><td class='mono'>0</td><td class='mono'>-</td><td class='mono'>-</td><td class='mono'>0.0</td><td class='mono'>0.0/min</td></tr></table></div>
50:<div class="panel"><h3>Decision HOLD Reason</h3><table><tr><td>Latest action</td><td class='mono'>HOLD</td></tr><tr><td>Latest HOLD interpretation</td><td class='mono'>HOLD_INFRA_OR_VIEW_DATA_INVALID</td></tr><tr><td>Latest reason/blocker</td><td class='mono'>view_data_invalid</td></tr><tr><td>Latest family/side</td><td class='mono'>-/FLAT</td></tr><tr><td>Latest safe/candidate fields</td><td class='mono'>safe_or_report=1 candidate_count=-</td></tr><tr><td>Sampled decisions</td><td class='mono'>40</td></tr><tr><td>Sampled span/rate</td><td class='mono'>4.8 min / 8.4 decisions per min</td></tr><tr><td>Action distribution</td><td class='mono'>HOLD=40</td></tr><tr><td>HOLD interpretation distribution</td><td class='mono'>HOLD_INFRA_OR_VIEW_DATA_INVALID=40</td></tr><tr><td>Paper status</td><td class='mono'>PAPER BLOCKED - dashboard never promotes paper</td></tr></table><table><tr><th>ID</th><th>Action</th><th>Interpretation</th><th>Reason/blocker</th><th>Family/side</th><th>Candidate count</th></tr><tr><td class='mono'>1777888475610-0</td><td class='mono'>HOLD</td><td class='mono'>HOLD_INFRA_OR_VIEW_DATA_INVALID</td><td class='mono'>view_data_invalid</td><td class='mono'>-/FLAT</td><td class='mono'>-</td></tr><tr><td class='mono'>1777888201259-0</td><td class='mono'>HOLD</td><td class='mono'>HOLD_INFRA_OR_VIEW_DATA_INVALID</td><td class='mono'>view_data_invalid</td><td class='mono'>-/FLAT</td><td class='mono'>-</td></tr><tr><td class='mono'>1777888201051-0</td><td class='mono'>HOLD</td><td class='mono'>HOLD_INFRA_OR_VIEW_DATA_INVALID</td><td class='mono'>view_data_invalid</td><td class='mono'>-/FLAT</td><td class='mono'>-</td></tr><tr><td class='mono'>1777888200827-0</td><td class='mono'>HOLD</td><td class='mono'>HOLD_INFRA_OR_VIEW_DATA_INVALID</td><td class='mono'>view_data_invalid</td><td class='mono'>-/FLAT</td><td class='mono'>-</td></tr><tr><td class='mono'>1777888200619-0</td><td class='mono'>HOLD</td><td class='mono'>HOLD_INFRA_OR_VIEW_DATA_INVALID</td><td class='mono'>view_data_invalid</td><td class='mono'>-/FLAT</td><td class='mono'>-</td></tr><tr><td class='mono'>1777888200414-0</td><td class='mono'>HOLD</td><td class='mono'>HOLD_INFRA_OR_VIEW_DATA_INVALID</td><td class='mono'>view_data_invalid</td><td class='mono'>-/FLAT</td><td class='mono'>-</td></tr></table></div>
53:<div style="display:none">OPS Dashboard R2C compatibility marker</div>

## Dashboard curl stderr

## Dashboard compile log

## pstatus post
{
  "broker_order_attempted": false,
  "classification": "PSTATUS_FAIL_CLOSED_RUNTIME_VERDICT_READY",
  "controlled_paper_route_imported": {
    "function": "build_fail_closed_controlled_paper_verdict",
    "import_ok": true,
    "result": {
      "allowed": false,
      "broker_live_blocked": true,
      "controlled_runtime_allowed": false,
      "observe_only": false,
      "paper_armed": false,
      "paper_enabled": false,
      "reason": "CONTROLLED_PAPER_RUNTIME_NOT_ALLOWED",
      "scope_ack_ok": false
    }
  },
  "created_at": "2026-06-14T05:38:04.517192+00:00",
  "env": {
    "B1_PROFIT_CLASSIC_RUNTIME_OBSERVE_ONLY": "1",
    "SCALPX_ALLOW_CONTROLLED_PAPER_RUNTIME": "",
    "SCALPX_CONTROLLED_PAPER_ARMED": "",
    "SCALPX_CONTROLLED_PAPER_SCOPE_ACK": "",
    "SCALPX_ENABLE_LIVE": "",
    "SCALPX_ENABLE_PAPER": "",
    "SCALPX_OBSERVE_ONLY": "1",
    "SCALPX_PAPER_ARMED": ""
  },
  "paper_live_enabled": false,
  "paper_runtime_verdict": {
    "controlled_runtime_allowed": false,
    "fail_closed": true,
    "live_enabled": false,
    "observe_only": true,
    "paper_armed": false,
    "paper_enabled": false,
    "paper_route_allowed": false,
    "position_flat_verified": false,
    "reason": "OBSERVE_ONLY_ACTIVE",
    "scope_ack_present": false
  },
  "project_root": "/home/Lenovo/scalpx/projects/mme_scalpx",
  "redis_delete_attempted": false,
  "redis_write_attempted": false,
  "safety": {
    "no_execution_stream": true,
    "no_order_stream": true,
    "no_risk_stream": true,
    "orders_risk_execution": "0/0/0",
    "processes": {
      "execution": 0,
      "replay": 0,
      "risk": 0
    },
    "risk_execution_not_running": true,
    "streams": {
      "execution": 0,
      "orders": 0,
      "risk": 0
    }
  },
  "schema_version": "pstatus_fail_closed_runtime_verdict_v1"
}

## pstatus post stderr
