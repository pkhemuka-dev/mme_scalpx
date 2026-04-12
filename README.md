# mme_scalpx

Clean development root for the MME ScalpX strategy platform.

## Structure
- app/mme_scalpx/core: spine and foundational modules
- app/mme_scalpx/domain: domain-specific project modules
- app/mme_scalpx/integrations: broker/login/token integrations
- app/mme_scalpx/services: runtime services
- app/mme_scalpx/ops: bootstrap and operational helpers

## Runtime
- Local Redis for current dev/test
- Future-compatible with remote TLS Redis cluster

## Secrets
Project secrets are linked from:
~/scalpx/common/secrets/projects/mme_scalpx
