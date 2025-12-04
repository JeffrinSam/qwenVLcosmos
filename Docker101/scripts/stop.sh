#!/bin/bash
# Stop Cosmos Predict 2.5 service

set -e

cd "$(dirname "$0")/.."

echo "Stopping Cosmos Predict 2.5..."

docker compose down

echo "✅ Service stopped"
