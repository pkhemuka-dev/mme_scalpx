# PDEV-HELPER-WRAPPERS-R1

Created repo wrapper files for shell helper commands so pdev can capture stable helper entrypoints.

## Helpers

- bin/pfeeds
- bin/pfeedcheck
- bin/pfeedstop
- bin/pstack
- bin/pstackcheck
- bin/pcheck
- bin/zlogin
- bin/plogin

## Safety

No service start, no Redis write/delete, no broker call, no order, no paper/live enablement.

## Note

Each wrapper sources ~/.bashrc and dispatches to the matching function/alias. It refuses alias self-recursion if an alias points back to bin/<helper>.
