#!/usr/bin/env sh
set -eu

PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "ERROR: .venv not found. Run ./setup.sh first."
  exit 1
fi

# shellcheck disable=SC1091
. "$VENV_DIR/bin/activate"

# Adiciona project_eva ao PYTHONPATH
export PYTHONPATH="$PROJECT_DIR/..:$PROJECT_DIR/../project_eva"

exec python "$PROJECT_DIR/app.py"
