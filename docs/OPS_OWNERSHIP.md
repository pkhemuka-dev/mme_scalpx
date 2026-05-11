# MME-ScalpX Ops Ownership

## app/mme_scalpx/ops/

Importable Python ops modules.

Allowed:
- healthcheck helpers
- bootstrap validation helpers
- preflight library functions
- session orchestration helpers

Not allowed:
- shell-only wrappers
- generated proof dumps
- one-off patch scripts

## ops/

Human/operator-facing helper scripts.

Allowed:
- manual inspection tools
- operator convenience scripts
- session management helpers

Not allowed:
- importable runtime business logic
- broker-order shortcuts
- hidden live enablement

## bin/ops/

Executable wrappers only.

Allowed:
- thin wrappers that call app/mme_scalpx/ops or ops scripts

Not allowed:
- duplicate business logic
- direct broker calls without runtime safety gates

## docs/ops/

Documentation only.
