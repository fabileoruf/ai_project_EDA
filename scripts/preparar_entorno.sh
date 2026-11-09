#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if command -v uv >/dev/null 2>&1; then
  if [[ ! -x .venv/bin/python ]]; then
    uv venv .venv
  fi
  uv pip install --python .venv/bin/python -r requirements.txt
else
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
fi

.venv/bin/python scripts/descargar_datos.py
printf '\nEntorno preparado. Abre notebooks/eda_covid19.ipynb y selecciona el Python de .venv.\n'
