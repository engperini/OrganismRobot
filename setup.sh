#!/usr/bin/env sh
set -eu

PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON_BIN=""

echo "==> Detecting Python..."

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  echo "ERROR: Python not found. Install Python 3 first."
  exit 1
fi

echo "==> Using: $PYTHON_BIN"

echo "==> Creating virtual environment..."
"$PYTHON_BIN" -m venv "$VENV_DIR"

echo "==> Activating virtual environment..."
# shellcheck disable=SC1091
. "$VENV_DIR/bin/activate"

echo "==> Upgrading pip/setuptools/wheel..."
python -m pip install --upgrade pip setuptools wheel

if [ -f "$PROJECT_DIR/requirements.txt" ]; then
  echo "==> Installing requirements..."
  pip install -r "$PROJECT_DIR/requirements.txt"
else
  echo "WARNING: requirements.txt not found, skipping dependency install."
fi

echo ""
echo "Setup complete."
echo "To activate later, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To start the app, run:"
echo "  python app.py"
