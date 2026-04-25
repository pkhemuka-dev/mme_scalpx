"""
LEGACY BASELINE MODULE — NOT A LIVE RUNTIME SERVICE.

Allowed use:
- frozen baseline replay
- shadow comparison
- rollback reference
- migration audit

Forbidden use:
- main.py canonical runtime service
- direct broker execution
- Redis decision publication
- production strategy promotion

Batch 20 quarantine law:
- this module may be imported only by explicit legacy/replay/quarantine proofs;
- this module must never appear in SERVICE_REGISTRY;
- this module must remain listed in main.py forbidden runtime paths;
- any future runtime activation attempt must fail closed.
"""

