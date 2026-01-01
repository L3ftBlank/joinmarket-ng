#!/bin/bash
# Wait for a service to be ready with exponential backoff
# Usage: wait-for-service.sh <service-name> <check-command> [max-attempts] [initial-delay]

set -e

SERVICE_NAME="${1:-service}"
CHECK_COMMAND="${2}"
MAX_ATTEMPTS="${3:-30}"
INITIAL_DELAY="${4:-2}"

if [ -z "$CHECK_COMMAND" ]; then
  echo "Usage: $0 <service-name> <check-command> [max-attempts] [initial-delay]"
  exit 1
fi

echo "Waiting for $SERVICE_NAME..."

attempt=0
delay=$INITIAL_DELAY

while [ $attempt -lt $MAX_ATTEMPTS ]; do
  attempt=$((attempt + 1))

  if eval "$CHECK_COMMAND" 2>/dev/null; then
    echo "✓ $SERVICE_NAME ready (attempt $attempt/$MAX_ATTEMPTS)"
    exit 0
  fi

  if [ $attempt -lt $MAX_ATTEMPTS ]; then
    echo "⏳ Attempt $attempt/$MAX_ATTEMPTS: $SERVICE_NAME not ready, waiting ${delay}s..."
    sleep $delay

    # Exponential backoff with max 10s
    delay=$((delay * 3 / 2))
    if [ $delay -gt 10 ]; then
      delay=10
    fi
  fi
done

echo "✗ Timeout waiting for $SERVICE_NAME after $MAX_ATTEMPTS attempts"
exit 1
