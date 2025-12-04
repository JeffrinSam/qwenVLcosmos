#!/bin/bash
# Validation script for Docker setup
# Checks prerequisites and validates configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Cosmos Predict 2.5 Docker Validation"
echo "=========================================="
echo ""

# Function to check command exists
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        return 1
    fi
}

# Function to check version
check_version() {
    local cmd=$1
    local min_version=$2
    local current_version=$($cmd)
    echo -e "${GREEN}  Version:${NC} $current_version"
}

# Check Docker
echo "1. Checking Docker..."
if check_command docker; then
    check_version "docker --version" "24.0"

    # Check if Docker daemon is running
    if docker info &> /dev/null; then
        echo -e "${GREEN}✓${NC} Docker daemon is running"
    else
        echo -e "${RED}✗${NC} Docker daemon is NOT running"
        echo -e "${YELLOW}  Fix:${NC} sudo systemctl start docker"
    fi
else
    echo -e "${YELLOW}  Install:${NC} curl -fsSL https://get.docker.com | sh"
fi
echo ""

# Check Docker Compose
echo "2. Checking Docker Compose..."
if check_command "docker compose"; then
    check_version "docker compose version" "2.20"
else
    echo -e "${YELLOW}  Install:${NC} sudo apt-get install docker-compose-plugin"
fi
echo ""

# Check NVIDIA driver
echo "3. Checking NVIDIA GPU..."
if check_command nvidia-smi; then
    echo -e "${GREEN}  GPU Info:${NC}"
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader | \
        awk '{print "    " $0}'

    # Check driver version (should be 565+)
    driver_version=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)
    driver_major=$(echo $driver_version | cut -d. -f1)
    if [ "$driver_major" -ge 565 ]; then
        echo -e "${GREEN}✓${NC} Driver version is sufficient (>= 565)"
    else
        echo -e "${YELLOW}⚠${NC} Driver version may be too old (< 565)"
    fi
else
    echo -e "${RED}✗${NC} NVIDIA driver not found"
    echo -e "${YELLOW}  Install:${NC} Follow NVIDIA driver installation guide"
fi
echo ""

# Check NVIDIA Docker runtime
echo "4. Checking NVIDIA Docker Runtime..."
if docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu24.04 nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓${NC} NVIDIA Docker runtime is working"
else
    echo -e "${RED}✗${NC} NVIDIA Docker runtime NOT working"
    echo -e "${YELLOW}  Install:${NC} sudo apt-get install nvidia-docker2"
    echo -e "${YELLOW}  Then:${NC} sudo systemctl restart docker"
fi
echo ""

# Check required directories
echo "5. Checking Required Directories..."
cd ..

dirs=(
    "Qwen_instructor_7B"
    "webinterfacemodule"
    "cosmos_predict2"
    "examples"
    "assets"
)

for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $dir exists"
    else
        echo -e "${RED}✗${NC} $dir NOT found"
    fi
done
echo ""

# Check Qwen model files
echo "6. Checking Qwen Model Files..."
if [ -d "Qwen_instructor_7B" ]; then
    model_files=$(find Qwen_instructor_7B -name "*.safetensors" 2>/dev/null | wc -l)
    if [ "$model_files" -gt 0 ]; then
        echo -e "${GREEN}✓${NC} Found $model_files model checkpoint files"
    else
        echo -e "${YELLOW}⚠${NC} No model files found"
        echo -e "${YELLOW}  Run:${NC} python3 Qwen_instructor_7B/download_qwen_instructor.py"
    fi

    # Check config files
    if [ -f "Qwen_instructor_7B/config.json" ]; then
        echo -e "${GREEN}✓${NC} config.json exists"
    else
        echo -e "${YELLOW}⚠${NC} config.json NOT found"
    fi
else
    echo -e "${RED}✗${NC} Qwen_instructor_7B directory not found"
fi
echo ""

# Check Python dependencies
echo "7. Checking Python Files..."
required_files=(
    "pyproject.toml"
    "uv.lock"
    "webinterfacemodule/app.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file exists"
    else
        echo -e "${RED}✗${NC} $file NOT found"
    fi
done
echo ""

# Check Docker files
echo "8. Checking Docker Files..."
cd Docker101

docker_files=(
    "Dockerfile"
    "docker-compose.yml"
    "README.md"
)

for file in "${docker_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file exists"
    else
        echo -e "${RED}✗${NC} $file NOT found"
    fi
done
echo ""

# Check disk space
echo "9. Checking Disk Space..."
available_space=$(df -BG . | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$available_space" -ge 100 ]; then
    echo -e "${GREEN}✓${NC} Sufficient disk space: ${available_space}GB available"
else
    echo -e "${YELLOW}⚠${NC} Low disk space: ${available_space}GB available (recommend 100GB+)"
fi
echo ""

# Check memory
echo "10. Checking System Memory..."
total_mem=$(free -g | awk '/^Mem:/ {print $2}')
if [ "$total_mem" -ge 32 ]; then
    echo -e "${GREEN}✓${NC} Sufficient RAM: ${total_mem}GB"
else
    echo -e "${YELLOW}⚠${NC} Low RAM: ${total_mem}GB (recommend 64GB+)"
fi
echo ""

# Validation summary
echo "=========================================="
echo "Validation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Fix any issues marked with ✗ or ⚠"
echo "2. Download Qwen model if not present:"
echo "   python3 ../Qwen_instructor_7B/download_qwen_instructor.py"
echo "3. Build Docker image:"
echo "   docker compose build"
echo "4. Start container:"
echo "   docker compose up -d"
echo "5. Access web interface:"
echo "   http://localhost:5000"
echo ""
