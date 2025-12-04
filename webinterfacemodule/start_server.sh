#!/bin/bash

# Cosmos Predict 2.5 Web Interface Launcher
# Usage: ./start_server.sh [port]

set -e

# Check for and activate virtual environment
VENV_PATH="../.venv"
if [ -d "$VENV_PATH" ] && [ -f "$VENV_PATH/bin/activate" ]; then
    echo "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🎬 Cosmos Predict 2.5 Web Interface Launcher           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running in correct directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}Error: app.py not found!${NC}"
    echo -e "Please run this script from the webinterfacemodule directory:"
    echo -e "  cd /home/humanoid/Downloads/cosmos-predict2.5/webinterfacemodule"
    echo -e "  ./start_server.sh"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"

# Check Flask installation
if ! python3 -c "import flask" 2>&1 | grep -q "ModuleNotFoundError"; then
    echo -e "${GREEN}✓${NC} Flask is installed"
else
    echo -e "${YELLOW}⚠${NC} Flask not installed. Installing dependencies..."

    # Check if UV is available (UV virtual environment)
    if command -v uv &> /dev/null; then
        echo -e "${YELLOW}→${NC} Using UV to install dependencies..."
        uv pip install -r requirements.txt
    # Check if we're in a conda environment
    elif [ -n "$CONDA_DEFAULT_ENV" ]; then
        echo -e "${YELLOW}→${NC} Detected conda environment, using conda install..."
        conda install -y flask flask-httpauth werkzeug -c conda-forge
    else
        # Try pip, fallback to --user if needed
        pip install -r requirements.txt 2>/dev/null || pip install --user -r requirements.txt
    fi
fi

# Create directories
mkdir -p uploads outputs
echo -e "${GREEN}✓${NC} Directories created"

# Get port (default 5000)
PORT=${1:-5000}

# Get IP address
IP=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Starting Cosmos Predict 2.5 Web Interface...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}Local Access:${NC}    http://localhost:$PORT"
echo -e "  ${GREEN}Network Access:${NC}  http://$IP:$PORT"
echo ""
echo -e "  ${YELLOW}Default Credentials:${NC}"
echo -e "    Username: admin"
echo -e "    Password: cosmos2025"
echo -e "    ${RED}⚠️  CHANGE THE PASSWORD IN app.py FOR SECURITY!${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start the server
export FLASK_APP=app.py
python3 app.py
