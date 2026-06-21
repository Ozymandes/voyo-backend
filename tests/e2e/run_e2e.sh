#!/usr/bin/env bash
# VOYO e2e runner — installs Playwright if missing, runs the 4-flow suite,
# and prints a per-flow PASS/FAIL summary suitable for the thesis appendix.
#
# Prereqs (user-run, not this script): full stack up —
#   backend :8000, docker-compose (OSRM+Valhalla+VROOM), Flutter web on :8099
#     cd flutter_app && flutter run -d web-server --web-port 8099
set -euo pipefail
cd "$(dirname "$0")/../.."

export VOYO_WEB_URL="${VOYO_WEB_URL:-http://localhost:8099}"

if ! python -c "import playwright" 2>/dev/null; then
  echo "▶ installing playwright…"
  pip install playwright >/dev/null
  python -m playwright install chromium
fi

echo "▶ running e2e suite against $VOYO_WEB_URL"
python -m pytest tests/e2e/test_demo_flows.py \
  -v -o addopts="" \
  --junitxml=data/evaluation/runs/e2e_junit.xml \
  "$@"
