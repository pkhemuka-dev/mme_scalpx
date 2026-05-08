# Batch 29BR — Active Config vs Archived Evidence Parse Audit

- Generated UTC: 2026-05-03T10:41:23.082814+00:00
- Active config verdict: FAIL
- Archive hygiene verdict: FAIL_ARCHIVE_PARSE_HYGIENE
- Active config parse errors: 0
- Archive parse errors: 3325
- Import errors: 14
- Compile app/bin/tests: {'app': True, 'bin': True, 'tests_present': True, 'tests': True}
- Code patch applied: false
- Broker calls executed: false
- Redis writes executed: false
- paper_armed verdict: BLOCKED
- real live verdict: BLOCKED

Conclusion: archived/redacted artifacts must be classified separately from active runtime config.
