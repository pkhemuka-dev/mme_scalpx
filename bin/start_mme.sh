#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# ScalpX MME - freeze-grade startup wrapper
#
# Purpose
# -------
# Thin operator wrapper around the canonical startup orchestrator:
#   mme_scalpx.ops.start_session
#
# Design rules
# ------------
# - loads the canonical env file
# - sets canonical PYTHONPATH
# - uses the project venv python
# - delegates startup policy to start_session.py
# - no hidden fallback logic
# ============================================================================

PROJECT_ROOT="/home/Lenovo/scalpx/projects/mme_scalpx"
APP_ROOT="${PROJECT_ROOT}/app"
ENV_FILE="${PROJECT_ROOT}/etc/project.env"
VENV_PY="${PROJECT_ROOT}/.venv/bin/python"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "ERROR: env file not found: ${ENV_FILE}" >&2
  exit 1
fi

if [[ ! -x "${VENV_PY}" ]]; then
  echo "ERROR: python executable not found or not executable: ${VENV_PY}" >&2
  exit 1
fi

cd "${PROJECT_ROOT}"
export PYTHONPATH="${APP_ROOT}"

set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a

MODE="systemd"
STRICT="--strict-preflight"

for arg in "$@"; do
  case "${arg}" in
    --direct)
      MODE="direct"
      ;;
    --systemd)
      MODE="systemd"
      ;;
    --no-strict-preflight)
      STRICT=""
      ;;
  esac
done

CMD=("${VENV_PY}" -m mme_scalpx.ops.start_session "--${MODE}")

if [[ -n "${STRICT}" ]]; then
  CMD+=("${STRICT}")
fi

for arg in "$@"; do
  case "${arg}" in
    --direct|--systemd|--no-strict-preflight)
      ;;
    *)
      CMD+=("${arg}")
      ;;
  esac
done

echo "RUN ${CMD[*]}"
exec "${CMD[@]}"
