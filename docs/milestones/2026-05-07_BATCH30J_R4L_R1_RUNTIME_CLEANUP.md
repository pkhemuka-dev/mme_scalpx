# Batch 30J-R4L-R1 — Runtime Cleanup After Final Safety Gate Blocker

Verdict: FAIL_STOP_AND_DIAGNOSE

Health: FAIL_STOP_AND_DIAGNOSE

Classification: R4L_RUNTIME_CLEANUP_FAILED_OR_NOT_SAFE

Selected dataset: run/replay/parity/offline_materialization/observe_only_replay_input_9c50b37fb4782fb0

Available dates: [
  "2026-04-29"
]

Cleanup performed: True

Cleanup actions: [
  {
    "pid": 23292,
    "service": "feeds",
    "cmdline_before": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap",
    "status_before": {
      "pid": 23292,
      "exists": true,
      "cmdline": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap",
      "state": "S (sleeping)",
      "status_tail": "Name:\tpython\nUmask:\t0002\nState:\tS (sleeping)\nTgid:\t23292\nNgid:\t0\nPid:\t23292\nPPid:\t23216\nTracerPid:\t0\nUid:\t1002\t1002\t1002\t1002\nGid:\t1003\t1003\t1003\t1003\nFDSize:\t64\nGroups:\t4 20 24 25 29 30 44 46 119 120 1000 1001 1003 \nNStgid:\t23292\nNSpid:\t23292\nNSpgid:\t23216\nNSsid:\t23057\nKthread:\t0\nVmPeak:\t  806564 kB\nVmSize:\t  444304 kB\nVmLck:\t       0 kB\nVmPin:\t       0 kB\nVmHWM:\t  790588 kB\nVmRSS:\t  286232 kB\nRssAnon:\t  265768 kB\nRssFile:\t   20464 kB\nRssShmem:\t       0 kB\nVmData:\t  281664 kB\nVmStk:\t     132 kB\nVmExe:\t    2772 kB\nVmLib:\t   14268 kB\nVmPTE:\t     660 kB\nVmSwap:\t       0 kB\nHugetlbPages:\t       0 kB\nCoreDumping:\t0\nTHP_enabled:\t1\nuntag_mask:\t0xffffffffffffffff\nThreads:\t3\nSigQ:\t0/63933\nSigPnd:\t0000000000000000\nShdPnd:\t0000000000000000\nSigBlk:\t0000000000000000\nSigIgn:\t0000000001001000\nSigCgt:\t0000000100004002\nCapInh:\t0000000000000000\nCapPrm:\t0000000000000000\nCapEff:\t0000000000000000\nCapBnd:\t000001ffffffffff\nCapAmb:\t0000000000000000\nNoNewPrivs:\t0\nSeccomp:\t0\nSeccomp_filters:\t0\nSpeculation_Store_Bypass:\tthread vulnerable\nSpeculationIndirectBranch:\tconditional enabled\nCpus_allowed:\tf\nCpus_allowed_list:\t0-3\nMems_allowed:\t00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000001\nMems_allowed_list:\t0\nvoluntary_ctxt_switches:\t30018\nnonvoluntary_ctxt_switches:\t874\nx86_Thread_features:\t\nx86_Thread_features_locked:\t\n",
      "is_app_main": true,
      "is_zombie": false,
      "classification": "LIVE_APP_MAIN_PROCESS"
    },
    "alive_before": true,
    "sigterm_sent": true,
    "sigkill_sent": false,
    "ok": true,
    "alive_after_term": true,
    "status_after_final": {
      "pid": 23292,
      "exists": true,
      "cmdline": "",
      "state": "Z (zombie)",
      "status_tail": "Name:\tpython\nState:\tZ (zombie)\nTgid:\t23292\nNgid:\t0\nPid:\t23292\nPPid:\t23216\nTracerPid:\t0\nUid:\t1002\t1002\t1002\t1002\nGid:\t1003\t1003\t1003\t1003\nFDSize:\t0\nGroups:\t4 20 24 25 29 30 44 46 119 120 1000 1001 1003 \nNStgid:\t23292\nNSpid:\t23292\nNSpgid:\t23216\nNSsid:\t23057\nKthread:\t0\nThreads:\t1\nSigQ:\t0/63933\nSigPnd:\t0000000000000000\nShdPnd:\t0000000000000000\nSigBlk:\t0000000000000000\nSigIgn:\t0000000001001000\nSigCgt:\t0000000100000000\nCapInh:\t0000000000000000\nCapPrm:\t0000000000000000\nCapEff:\t0000000000000000\nCapBnd:\t000001ffffffffff\nCapAmb:\t0000000000000000\nNoNewPrivs:\t0\nSeccomp:\t0\nSeccomp_filters:\t0\nSpeculation_Store_Bypass:\tthread vulnerable\nSpeculationIndirectBranch:\tconditional enabled\nCpus_allowed:\tf\nCpus_allowed_list:\t0-3\nMems_allowed:\t00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000001\nMems_allowed_list:\t0\nvoluntary_ctxt_switches:\t30023\nnonvoluntary_ctxt_switches:\t876\nx86_Thread_features:\t\nx86_Thread_features_locked:\t\n",
      "is_app_main": false,
      "is_zombie": true,
      "classification": "ZOMBIE_OR_EXITED_PROCESS_REMAINS"
    },
    "alive_after_final": true
  },
  {
    "pid": 23293,
    "service": "features",
    "cmdline_before": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service features --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap",
    "status_before": {
      "pid": 23293,
      "exists": true,
      "cmdline": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service features --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap",
      "state": "R (running)",
      "status_tail": "Name:\tpython\nUmask:\t0002\nState:\tR (running)\nTgid:\t23293\nNgid:\t0\nPid:\t23293\nPPid:\t23216\nTracerPid:\t0\nUid:\t1002\t1002\t1002\t1002\nGid:\t1003\t1003\t1003\t1003\nFDSize:\t64\nGroups:\t4 20 24 25 29 30 44 46 119 120 1000 1001 1003 \nNStgid:\t23293\nNSpid:\t23293\nNSpgid:\t23216\nNSsid:\t23057\nKthread:\t0\nVmPeak:\t  806560 kB\nVmSize:\t  316292 kB\nVmLck:\t       0 kB\nVmPin:\t       0 kB\nVmHWM:\t  790664 kB\nVmRSS:\t  303580 kB\nRssAnon:\t  283956 kB\nRssFile:\t   19624 kB\nRssShmem:\t       0 kB\nVmData:\t  284192 kB\nVmStk:\t     132 kB\nVmExe:\t    2772 kB\nVmLib:\t   14268 kB\nVmPTE:\t     684 kB\nVmSwap:\t       0 kB\nHugetlbPages:\t       0 kB\nCoreDumping:\t0\nTHP_enabled:\t1\nuntag_mask:\t0xffffffffffffffff\nThreads:\t1\nSigQ:\t0/63933\nSigPnd:\t0000000000000000\nShdPnd:\t0000000000000000\nSigBlk:\t0000000000000000\nSigIgn:\t0000000001001000\nSigCgt:\t0000000000004002\nCapInh:\t0000000000000000\nCapPrm:\t0000000000000000\nCapEff:\t0000000000000000\nCapBnd:\t000001ffffffffff\nCapAmb:\t0000000000000000\nNoNewPrivs:\t0\nSeccomp:\t0\nSeccomp_filters:\t0\nSpeculation_Store_Bypass:\tthread vulnerable\nSpeculationIndirectBranch:\tconditional enabled\nCpus_allowed:\tf\nCpus_allowed_list:\t0-3\nMems_allowed:\t00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000001\nMems_allowed_list:\t0\nvoluntary_ctxt_switches:\t1466\nnonvoluntary_ctxt_switches:\t991\nx86_Thread_features:\t\nx86_Thread_features_locked:\t\n",
      "is_app_main": true,
      "is_zombie": false,
      "classification": "LIVE_APP_MAIN_PROCESS"
    },
    "alive_before": true,
    "sigterm_sent": true,
    "sigkill_sent": false,
    "ok": false,
    "alive_after_term": true,
    "alive_after_final": true,
    "status_after_final": {
      "pid": 23293,
      "exists": true,
      "cmdline": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service features --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap",
      "state": "R (running)",
      "status_tail": "Name:\tpython\nUmask:\t0002\nState:\tR (running)\nTgid:\t23293\nNgid:\t0\nPid:\t23293\nPPid:\t23216\nTracerPid:\t0\nUid:\t1002\t1002\t1002\t1002\nGid:\t1003\t1003\t1003\t1003\nFDSize:\t64\nGroups:\t4 20 24 25 29 30 44 46 119 120 1000 1001 1003 \nNStgid:\t23293\nNSpid:\t23293\nNSpgid:\t23216\nNSsid:\t23057\nKthread:\t0\nVmPeak:\t  806560 kB\nVmSize:\t  313220 kB\nVmLck:\t       0 kB\nVmPin:\t       0 kB\nVmHWM:\t  790664 kB\nVmRSS:\t  301096 kB\nRssAnon:\t  281472 kB\nRssFile:\t   19624 kB\nRssShmem:\t       0 kB\nVmData:\t  281120 kB\nVmStk:\t     132 kB\nVmExe:\t    2772 kB\nVmLib:\t   14268 kB\nVmPTE:\t     684 kB\nVmSwap:\t       0 kB\nHugetlbPages:\t       0 kB\nCoreDumping:\t0\nTHP_enabled:\t1\nuntag_mask:\t0xffffffffffffffff\nThreads:\t1\nSigQ:\t0/63933\nSigPnd:\t0000000000000000\nShdPnd:\t0000000000000000\nSigBlk:\t0000000000000000\nSigIgn:\t0000000001001000\nSigCgt:\t0000000000004002\nCapInh:\t0000000000000000\nCapPrm:\t0000000000000000\nCapEff:\t0000000000000000\nCapBnd:\t000001ffffffffff\nCapAmb:\t0000000000000000\nNoNewPrivs:\t0\nSeccomp:\t0\nSeccomp_filters:\t0\nSpeculation_Store_Bypass:\tthread vulnerable\nSpeculationIndirectBranch:\tconditional enabled\nCpus_allowed:\tf\nCpus_allowed_list:\t0-3\nMems_allowed:\t00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000001\nMems_allowed_list:\t0\nvoluntary_ctxt_switches:\t1472\nnonvoluntary_ctxt_switches:\t1005\nx86_Thread_features:\t\nx86_Thread_features_locked:\t\n",
      "is_app_main": true,
      "is_zombie": false,
      "classification": "LIVE_APP_MAIN_PROCESS"
    }
  },
  {
    "pid": 23296,
    "service": "strategy",
    "cmdline_before": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service strategy --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap",
    "status_before": {
      "pid": 23296,
      "exists": true,
      "cmdline": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service strategy --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap",
      "state": "R (running)",
      "status_tail": "Name:\tpython\nUmask:\t0002\nState:\tR (running)\nTgid:\t23296\nNgid:\t0\nPid:\t23296\nPPid:\t23216\nTracerPid:\t0\nUid:\t1002\t1002\t1002\t1002\nGid:\t1003\t1003\t1003\t1003\nFDSize:\t64\nGroups:\t4 20 24 25 29 30 44 46 119 120 1000 1001 1003 \nNStgid:\t23296\nNSpid:\t23296\nNSpgid:\t23216\nNSsid:\t23057\nKthread:\t0\nVmPeak:\t  807592 kB\nVmSize:\t  302996 kB\nVmLck:\t       0 kB\nVmPin:\t       0 kB\nVmHWM:\t  790824 kB\nVmRSS:\t  289940 kB\nRssAnon:\t  270264 kB\nRssFile:\t   19676 kB\nRssShmem:\t       0 kB\nVmData:\t  270896 kB\nVmStk:\t     132 kB\nVmExe:\t    2772 kB\nVmLib:\t   14268 kB\nVmPTE:\t     648 kB\nVmSwap:\t       0 kB\nHugetlbPages:\t       0 kB\nCoreDumping:\t0\nTHP_enabled:\t1\nuntag_mask:\t0xffffffffffffffff\nThreads:\t1\nSigQ:\t0/63933\nSigPnd:\t0000000000000000\nShdPnd:\t0000000000000000\nSigBlk:\t0000000000000000\nSigIgn:\t0000000001001000\nSigCgt:\t0000000000004002\nCapInh:\t0000000000000000\nCapPrm:\t0000000000000000\nCapEff:\t0000000000000000\nCapBnd:\t000001ffffffffff\nCapAmb:\t0000000000000000\nNoNewPrivs:\t0\nSeccomp:\t0\nSeccomp_filters:\t0\nSpeculation_Store_Bypass:\tthread vulnerable\nSpeculationIndirectBranch:\tconditional enabled\nCpus_allowed:\tf\nCpus_allowed_list:\t0-3\nMems_allowed:\t00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000001\nMems_allowed_list:\t0\nvoluntary_ctxt_switches:\t3306\nnonvoluntary_ctxt_switches:\t787\nx86_Thread_features:\t\nx86_Thread_features_locked:\t\n",
      "is_app_main": true,
      "is_zombie": false,
      "classification": "LIVE_APP_MAIN_PROCESS"
    },
    "alive_before": true,
    "sigterm_sent": true,
    "sigkill_sent": false,
    "ok": true,
    "alive_after_term": true,
    "status_after_final": {
      "pid": 23296,
      "exists": true,
      "cmdline": "",
      "state": "Z (zombie)",
      "status_tail": "Name:\tpython\nState:\tZ (zombie)\nTgid:\t23296\nNgid:\t0\nPid:\t23296\nPPid:\t23216\nTracerPid:\t0\nUid:\t1002\t1002\t1002\t1002\nGid:\t1003\t1003\t1003\t1003\nFDSize:\t0\nGroups:\t4 20 24 25 29 30 44 46 119 120 1000 1001 1003 \nNStgid:\t23296\nNSpid:\t23296\nNSpgid:\t23216\nNSsid:\t23057\nKthread:\t0\nThreads:\t1\nSigQ:\t0/63933\nSigPnd:\t0000000000000000\nShdPnd:\t0000000000000000\nSigBlk:\t0000000000000000\nSigIgn:\t0000000001001000\nSigCgt:\t0000000000000000\nCapInh:\t0000000000000000\nCapPrm:\t0000000000000000\nCapEff:\t0000000000000000\nCapBnd:\t000001ffffffffff\nCapAmb:\t0000000000000000\nNoNewPrivs:\t0\nSeccomp:\t0\nSeccomp_filters:\t0\nSpeculation_Store_Bypass:\tthread vulnerable\nSpeculationIndirectBranch:\tconditional enabled\nCpus_allowed:\tf\nCpus_allowed_list:\t0-3\nMems_allowed:\t00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000001\nMems_allowed_list:\t0\nvoluntary_ctxt_switches:\t3311\nnonvoluntary_ctxt_switches:\t791\nx86_Thread_features:\t\nx86_Thread_features_locked:\t\n",
      "is_app_main": false,
      "is_zombie": true,
      "classification": "ZOMBIE_OR_EXITED_PROCESS_REMAINS"
    },
    "alive_after_final": true
  }
]

Blockers: [
  "CLEANUP_ACTIONS_ALL_OK_BLOCKER"
]

Review: [
  "FEATURES_STREAM_MOVED_DURING_RUNTIME_CLEANUP",
  "DECISIONS_STREAM_MOVED_DURING_RUNTIME_CLEANUP",
  "ONLY_ONE_SELECTOR_DATE_AVAILABLE_ACCEPTED_FOR_CONTROLLED_NEXT_STEP"
]

Next: Do not execute replay. Inspect 30J-R4L-R1 blockers first.

Safety: no replay execution, no metadata mutation, no Redis key/lock deletion, no Redis restart, no paper/live, no orders. Only guarded SIGTERM of app.mme_scalpx.main runtime owners when eligible.
