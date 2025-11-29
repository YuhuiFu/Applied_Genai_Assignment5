#!/usr/bin/env bash
set -e

VENV_DIR=${VENV_DIR:-.venv}

if [ -d "$VENV_DIR" ]; then
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
fi

python multi_agent_system.py
