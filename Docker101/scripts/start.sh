#!/bin/bash
# Start Cosmos Predict 2.5 service

set -e

cd "$(dirname "$0")/.."

echo "Starting Cosmos Predict 2.5..."

# Start service
docker compose up -d

# Wait for service to be healthy
echo "Waiting for service to be healthy..."
sleep 10

# Check status
if docker compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Cosmos Predict 2.5 is running!"
    echo ""
    echo "   Web Interface: http://localhost:5000"
    echo "   Login: admin / cosmos2025"
    echo ""
    echo "View logs:"
    echo "   docker compose logs -f"
    echo ""
else
    echo "❌ Failed to start service"
    echo "Check logs:"
    echo "   docker compose logs"
    exit 1
fi
