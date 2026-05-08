Batch 26-O6 - Lightweight Observer Guard

Purpose:
- one observer only
- no heavy Redis calls
- no HGETALL state:features:mme:fut loop
- no XREVRANGE COUNT greater than 1
- poll every 30 seconds or slower
- stop if Redis latency exceeds 2 seconds
- stop if disk exceeds 85 percent
- write compact JSONL only

Live command:
cd /home/Lenovo/scalpx/projects/mme_scalpx
.venv/bin/python bin/live_signal_forensics_observer.py --run --duration-sec 1800 --poll-sec 30 --redis-timeout-sec 2 --disk-max-pct 85
