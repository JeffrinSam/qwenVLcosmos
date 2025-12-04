#!/bin/bash
# Build Docker image for Cosmos Predict 2.5

set -e

echo "================================================================================"
echo " Building Cosmos Predict 2.5 Docker Image (RTX 5090 Optimized)"
echo "================================================================================"

cd "$(dirname "$0")/.."

# Enable BuildKit for better caching
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build with progress
docker compose build --progress=plain

echo ""
echo "✅ Build complete!"
echo ""
echo "Next steps:"
echo "  docker compose up -d              # Start in background"
echo "  docker compose up                 # Start with logs"
echo "  docker compose logs -f            # View logs"
echo ""
