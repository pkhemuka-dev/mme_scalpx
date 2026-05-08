# Batch 30J-R4I-R1 — Runtime Cleanup After Selector Probe Contamination

Verdict: PASS_GREEN_CONTINUE

Health: GREEN_CONTINUE

Classification: R4I_RUNTIME_CONTAMINATION_CLEANED_READY_FOR_CLEAN_SELECTOR_PROBE

Cleanup performed: True

Cleanup actions: [
  {
    "pid": 22251,
    "reason": "Lane C offline selector/replay isolation cleanup after 30J-R4I; service=feeds",
    "cmdline_before": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap",
    "status_before": {
      "pid": 22251,
      "exists": true,
      "cmdline": "/home/Lenovo/scalpx/projects/mme_scalpx/.venv/bin/python -m app.mme_scalpx.main --service feeds --bootstrap-provider app.mme_scalpx.integrations.bootstrap_provider:provide --skip-group-bootstrap",
      "status_tail": "Name:\tpython\nUmask:\t0002\nState:\tR (running)\nTgid:\t22251\nNgid:\t0\nPid:\t22251\nPPid:\t1\nTracerPid:\t0\nUid:\t1002\t1002\t1002\t1002\nGid:\t1003\t1003\t1003\t1003\nFDSize:\t256\nGroups:\t4 20 24 25 29 30 44 46 119 120 1000 1001 1003 \nNStgid:\t22251\nNSpid:\t22251\nNSpgid:\t22251\nNSsid:\t19031\nKthread:\t0\nVmPeak:\t  806576 kB\nVmSize:\t  489988 kB\nVmLck:\t       0 kB\nVmPin:\t       0 kB\nVmHWM:\t  790692 kB\nVmRSS:\t  331576 kB\nRssAnon:\t  311192 kB\nRssFile:\t   20384 kB\nRssShmem:\t       0 kB\nVmData:\t  327352 kB\nVmStk:\t     132 kB\nVmExe:\t    2772 kB\nVmLib:\t   14268 kB\nVmPTE:\t     736 kB\nVmSwap:\t       0 kB\nHugetlbPages:\t       0 kB\nCoreDumping:\t0\nTHP_enabled:\t1\nuntag_mask:\t0xffffffffffffffff\nThreads:\t3\nSigQ:\t0/63933\nSigPnd:\t0000000000000000\nShdPnd:\t0000000000000000\nSigBlk:\t0000000000000000\nSigIgn:\t0000000001001001\nSigCgt:\t0000000100004002\nCapInh:\t0000000000000000\nCapPrm:\t0000000000000000\nCapEff:\t0000000000000000\nCapBnd:\t000001ffffffffff\nCapAmb:\t0000000000000000\nNoNewPrivs:\t0\nSeccomp:\t0\nSeccomp_filters:\t0\nSpeculation_Store_Bypass:\tthread vulnerable\nSpeculationIndirectBranch:\tconditional enabled\nCpus_allowed:\tf\nCpus_allowed_list:\t0-3\nMems_allowed:\t00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000000,00000001\nMems_allowed_list:\t0\nvoluntary_ctxt_switches:\t36808\nnonvoluntary_ctxt_switches:\t255\nx86_Thread_features:\t\nx86_Thread_features_locked:\t\n",
      "state": "R (running)",
      "is_app_main": true,
      "is_zombie": false,
      "classification": "LIVE_APP_MAIN_PROCESS"
    },
    "alive_before": true,
    "sigterm_sent": true,
    "sigkill_sent": false,
    "alive_after_term": false,
    "alive_after_final": false,
    "status_after_final": {
      "pid": 22251,
      "exists": false,
      "classification": "PID_ABSENT"
    },
    "ok": true
  }
]

Blockers: []

Review: []

Next: Batch 30J-R4I-R2 — rerun source-specific selector probe under clean offline isolation; no install, no replay execution.

Safety: no replay execution, no selector metadata install, no Redis key/lock deletion, no Redis restart, no paper/live, no orders. Only guarded SIGTERM of app.mme_scalpx.main runtime owners if eligible.
