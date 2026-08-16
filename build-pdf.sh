#!/usr/bin/env bash
# Regenerate both PDFs from source:
#   Kirill_Demidov_CV.pdf      — designed two-column version (index.html)
#   Kirill_Demidov_CV_ATS.pdf  — single-column ATS-safe version (cv-ats.html)
# Run after editing index.html / index.css / the JSON resume, then commit the output.
set -euo pipefail

cd "$(dirname "$0")"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ -x "$CHROME" ] || { echo "Chrome not found at $CHROME" >&2; exit 1; }

# index.html, cv-ats.html and the .txt version all come from the JSON resume
python3 build.py
python3 build-ats.py

render() {
  "$CHROME" --headless --disable-gpu --no-pdf-header-footer \
    --virtual-time-budget=5000 \
    --print-to-pdf="$2" \
    "file://$PWD/$1" 2>/dev/null
  echo "$2 regenerated"
}

render index.html Kirill_Demidov_CV.pdf
render cv-ats.html Kirill_Demidov_CV_ATS.pdf
