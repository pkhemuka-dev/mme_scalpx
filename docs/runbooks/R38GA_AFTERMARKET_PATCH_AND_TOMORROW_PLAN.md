# R38GA After-Market Patch and Tomorrow Plan

Use R38GA, not R38EN.

R38GA logic:
1. Keep observe strategy alive.
2. Find real observed candidate.
3. Start execution and risk with the same generated exact-scope ACK.
4. Risk.py now accepts generated exact-scope ACK as controlled-paper ACK.
5. Wait until risk gate is open:
   - veto_entries=0
   - max_new_lots>=1
   - strategy_heartbeat_fresh=1
   - execution_heartbeat_fresh=1
6. Stop strategy only after risk opens.
7. Isolate decisions stream.
8. Inject exactly one metadata-contract projected row.
9. Watch one event only.
10. Trap always restores fail-closed and observe strategy.

Tomorrow commands:
bash bin/r38ga_aftermarket_audit_no_start.sh
bash bin/r38ga_keep_strategy_until_risk_open_one_event.sh
