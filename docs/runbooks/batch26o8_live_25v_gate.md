Batch 26-O8 - Live 25V Gate Aggregator

Purpose:
Run one clean live market gate before controlled paper.

It aggregates:
- provider runtime proof
- feed snapshot proof
- feature payload proof
- family surfaces proof
- strategy activation proof
- no-order proof

Install proof:
.venv/bin/python bin/run_batch26o8_live_25v_gate.py --install-proof

Tomorrow live command:
BATCH25V_OBSERVE_SECONDS=60 .venv/bin/python bin/run_batch26o8_live_25v_gate.py --run --observe-seconds 60 --timeout-sec 120

Controlled paper remains blocked unless:
batch26o8_live_25v_gate_ok = true
