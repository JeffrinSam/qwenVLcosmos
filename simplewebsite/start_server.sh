#!/bin/bash

# Cosmos Predict 2.5 - Simple Web Interface
# Server startup script

cd "$(dirname "$0")"

echo "========================================"
echo "Cosmos Predict 2.5 Web Interface"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Get local IP address for network access
LOCAL_IP=$(hostname -I | awk '{print $1}')

echo "========================================"
echo "           SERVER STARTING"
echo "========================================"
echo ""
echo "Access URLs:"
echo "  Local:   http://127.0.0.1:5000"
echo "  Network: http://$LOCAL_IP:5000"
echo ""
echo "Authentication:"
echo "  Username: admin"
echo "  Password: cosmos2025"
echo ""
echo "Files will be saved to:"
echo "  Uploads: $(pwd)/uploads/"
echo "  Outputs: $(pwd)/outputs/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Make app.py executable
chmod +x app.py

# Run Flask app
python3 app.py
