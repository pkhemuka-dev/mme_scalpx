# B1-PROFIT-LIVE-R37M-R1_INTEGRATE_RECORDER_STATUS_INTO_PCHECK_NO_ORDER

Classification: **PASS_R37M_R1_PCHECK_INTEGRATES_RECORDER_STATUS_NO_ORDER**

Integrated R37M emergency durable-recorder status into `pcheck`.

`pcheck5min` is now only a compatibility wrapper that calls `pcheck`.

No service start.  
No service stop.  
No process kill.  
No Redis delete/write.  
No risk start.  
No execution start.  
No order.

Proof: `run/proofs/B1-PROFIT-LIVE-R37M-R1_INTEGRATE_RECORDER_STATUS_INTO_PCHECK_NO_ORDER_wrap_pcheck_with_r37m_recorder_visibility_readonly_no_start_no_order_20260527_093211.json`
