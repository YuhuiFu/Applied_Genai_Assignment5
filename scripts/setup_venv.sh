#!/usr/bin/env bash
set -e

PYTHON=${PYTHON:-python3}
VENV_DIR=${VENV_DIR:-.venv}

echo "Creating virtual environment in $VENV_DIR..."
$PYTHON -m venv "$VENV_DIR"

echo "Activating virtual environment..."
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

echo "Upgrading pip and installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Done."
echo "To activate this environment later, run:"
echo "  source $VENV_DIR/bin/activate"
