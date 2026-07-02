# R35C_R4D_ONE_DAY_CAPPED_REPLAY_SUMMARY_PATCH_VERIFY_20260601_NO_ORDER_20260613_221414

classification: REVIEW_R35C_R4D_REPLAY_OR_SUMMARY_PATCH_VERIFY_NEEDS_INSPECTION_NO_ORDER
proof: `run/proofs/R35C_R4D_ONE_DAY_CAPPED_REPLAY_SUMMARY_PATCH_VERIFY_20260601_NO_ORDER_20260613_221414.json`
run_root: `run/replay/r35c_r4d/20260613_221414`
summary_json: ``
summary_csv: ``

compile_rc=0 replay_rc=148 big_files_over_50mb=0
safety pre=0/0/0 post=0/0/0 proc=0/0 replay_proc=2

## Largest files

## Run summary JSON

## Run summary CSV

## Engine result

## Replay log tail
Traceback (most recent call last):
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3655, in <module>
    raise SystemExit(main(sys.argv[1:]))
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3362, in main
    engine_result = engine.execute(
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/engine.py", line 199, in execute
    self._execute_stage(context, stage, stage_executor)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/engine.py", line 477, in _batch16_execute_stage
    return _BATCH16_ORIGINAL_EXECUTE_STAGE(self, context, stage, guarded_executor)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/engine.py", line 239, in _execute_stage
    raw_output = stage_executor(context, stage)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/engine.py", line 468, in guarded_executor
    raw = stage_executor(ctx, st)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 3131, in stage_executor
    decisions = build_strategy_decisions_from_feature_frames(
  File "/home/Lenovo/scalpx/projects/mme_scalpx/bin/replay_run.py", line 2056, in build_strategy_decisions_from_feature_frames
    result = _r31a_strategy_adapter(run_id=str(run_id), feature_payload=feature_payload)
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/strategy_adapter.py", line 237, in build_replay_strategy_decision_payload
    "candidate_json": _canonical_json(candidates),
  File "/home/Lenovo/scalpx/projects/mme_scalpx/app/mme_scalpx/replay/strategy_adapter.py", line 73, in _canonical_json
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
  File "/usr/lib/python3.10/json/__init__.py", line 238, in dumps
    **kw).encode(obj)
  File "/usr/lib/python3.10/json/encoder.py", line 199, in encode
    chunks = self.iterencode(o, _one_shot=True)
  File "/usr/lib/python3.10/json/encoder.py", line 257, in iterencode
    return _iterencode(o, 0)
KeyboardInterrupt

## Compile log
