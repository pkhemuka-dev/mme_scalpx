# MME Systemd Runtime Unit Registry

Batch: 20  
Status: freeze governance surface

## Law

Only canonical runtime units may be used for unattended runtime. Helper or historical units must be classified before use.

| unit | status | owner | allowed_to_start_manually | allowed_in_production | canonical_replacement | reason |
|---|---|---|---:|---:|---|---|
| scalpx-mme.service | canonical_runtime | ops | true | true | n/a | canonical `python -m app.mme_scalpx.main` runtime |
| scalpx-mme-feeds-collector.service | historical_or_helper | ops | false | false | scalpx-mme.service | old/helper feed collector surface; not canonical runtime |
| scalpx-mme-open.service | historical_or_helper | ops | false | false | ops/start_session.py or canonical runtime command | old open-session helper |
| scalpx-mme-close.service | historical_or_helper | ops | false | false | ops/stop_session.py or canonical runtime command | old close-session helper |

## Required proof

`bin/proof_repo_hygiene_quarantine.py` and future ops proof must verify that only canonical units are documented as production-allowed.
