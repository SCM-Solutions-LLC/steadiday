#!/usr/bin/env bash
#
# Run the accessibility audit locally.
#
# Handles the three things audit_a11y.mjs cannot do for itself: installing its
# two dependencies, serving the site, and shutting the server down afterwards.
#
#   scripts/audit.sh                          # audit everything
#   scripts/audit.sh index.html pricing.html  # audit specific pages
#
# Env:
#   AUDIT_PORT  port for the local server (default 8899; auto-bumped if taken)
#   BASE_URL    audit an already-running server instead, and skip serving
#   SKIP_AXE=1  skip the axe layer

set -euo pipefail

cd "$(dirname "$0")/.."

# playwright-core rather than playwright: the audit never needs a bundled
# browser download, and audit_a11y.mjs finds a system Chromium on its own.
if ! node -e "require.resolve('playwright-core'); require.resolve('axe-core')" 2>/dev/null; then
  echo "installing playwright-core and axe-core…"
  npm install --no-save playwright-core@1.49.0 axe-core@4.13.0
fi

# An externally supplied BASE_URL means someone else owns the server.
if [ -n "${BASE_URL:-}" ]; then
  exec node scripts/audit_a11y.mjs "$@"
fi

port="${AUDIT_PORT:-8899}"
while nc -z localhost "$port" 2>/dev/null; do
  echo "port $port is busy, trying $((port + 1))"
  port=$((port + 1))
done

python3 -m http.server "$port" --directory . >/dev/null 2>&1 &
server=$!
trap 'kill "$server" 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  curl -sf -o /dev/null "http://localhost:$port/index.html" && break
  sleep 1
done
if ! curl -sf -o /dev/null "http://localhost:$port/index.html"; then
  echo "server never came up on port $port" >&2
  exit 1
fi

BASE_URL="http://localhost:$port" node scripts/audit_a11y.mjs "$@"
