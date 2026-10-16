#!/usr/bin/env bash
# Generates API traffic for the Grafana panels and to push backend CPU up for the HPA demo.
# Usage: URL=http://stockpilot.local ./scripts/load-test.sh [requests] [parallel]
set -euo pipefail
URL="${URL:-http://stockpilot.local}"
REQUESTS="${1:-3000}"
PARALLEL="${2:-20}"

echo "Sending ${REQUESTS} requests to ${URL} with ${PARALLEL} workers..."
seq "${REQUESTS}" | xargs -P "${PARALLEL}" -I{} sh -c '
  curl -s -o /dev/null "'"${URL}"'/api/products"
  curl -s -o /dev/null "'"${URL}"'/api/products/stats"
  curl -s -o /dev/null "'"${URL}"'/api/products/999999"
'
echo "Done. Watch: kubectl get hpa -n stockpilot -w"
