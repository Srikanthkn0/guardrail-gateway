#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -x venv/bin/uvicorn ]]; then
  echo "Missing venv. Run:"
  echo "  python3 -m venv venv"
  echo "  ./venv/bin/pip install -r requirements.txt"
  exit 1
fi

PORT="${PORT:-8000}"
echo "Starting Guardrail Gateway on http://127.0.0.1:${PORT}"
exec ./venv/bin/uvicorn app.main:app --reload --reload-dir app --port "${PORT}"