#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/run_e2e.sh [<playwright-args>]
# Ensures uvicorn runs with the project's venv Python, runs Playwright, and tears down the server.

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# Check venv
if [ ! -x "./venv/bin/python" ]; then
  echo "Virtualenv not found at ./venv. Create it with:\n  python3 -m venv venv\n  source venv/bin/activate\n  pip install -r requirements.txt"
  exit 1
fi

# Start uvicorn using the venv's python
echo "Starting uvicorn with venv python..."
./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 &
UVICORN_PID=$!

# Ensure we stop uvicorn on exit
cleanup() {
  echo "Stopping uvicorn (pid $UVICORN_PID)..."
  kill "$UVICORN_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Wait a little for the server to be ready
sleep 1

# Run Playwright tests (forward any extra args)
if ! command -v npx >/dev/null 2>&1; then
  echo "npx not found. Please install Node.js and Playwright: npm install --save-dev @playwright/test && npx playwright install"
  exit 1
fi

NPX_ARGS=("tests/e2e/bread-calculation.spec.js" "--reporter=list" "--workers=1")
if [ "$#" -gt 0 ]; then
  NPX_ARGS=("$@")
fi

npx playwright test "${NPX_ARGS[@]}"

# When Playwright finishes, the trap will stop uvicorn
