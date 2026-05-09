#!/usr/bin/env bash
set -euo pipefail

if ! python -c "import spacy" >/dev/null 2>&1; then
  echo "spaCy is not installed. Install dependencies first." >&2
  exit 1
fi

echo "Installing spaCy model en_core_web_sm..."
python -m spacy download en_core_web_sm
echo "Done."
