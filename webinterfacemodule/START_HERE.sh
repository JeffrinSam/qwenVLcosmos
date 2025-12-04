#!/bin/bash

# ========================================================================
# Cosmos Predict 2.5 Web Interface Startup Script
# ========================================================================

cd "$(dirname "$0")"

# Kill any existing Flask servers on port 5000
echo "Checking for existing servers..."
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
sleep 1

# Use the virtual environment
PYTHON_PATH="../.venv/bin/python3"

if [ ! -f "$PYTHON_PATH" ]; then
    echo "Error: Virtual environment not found at $PYTHON_PATH"
    echo "Please run setup first."
    exit 1
fi

echo ""
echo "========================================================================"
echo "🎬 Starting Cosmos Predict 2.5 Web Interface"
echo "========================================================================"
echo ""
echo "Updated with validated pipelines:"
echo "  ✅ SO-1 Arm (LeRobot)"
echo "  ✅ 2-Wheel Mobile Robot (UGV)"
echo "  ✅ Bimanual UR3"
echo "  ✅ General Image Analyzer"
echo ""
echo "New Feature: --disable-guardrails enabled for robotics prompts"
echo ""
echo "Access the interface at:"
echo "  http://localhost:5000"
echo "  http://YOUR_IP:5000 (for network access)"
echo ""
echo "Authentication: Disabled (AUTH_ENABLED = False in app.py)"
echo ""
echo "========================================================================"
echo ""

# Start the Flask server
$PYTHON_PATH app.py

# Cleanup on exit
trap "echo 'Shutting down...'; lsof -ti:5000 | xargs kill -9 2>/dev/null || true" EXIT
