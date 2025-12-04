#!/bin/bash
# Validate Docker101 setup

set -e

cd "$(dirname "$0")/.."

echo "================================================================================"
echo " Validating Docker101 Setup"
echo "================================================================================"
echo ""

# Check required files
echo "Checking required files..."
files=(
    "Dockerfile"
    "docker-compose.yml"
    "README.md"
    ".env.example"
    "scripts/build.sh"
    "scripts/start.sh"
    "scripts/stop.sh"
)

missing=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING)"
        missing=1
    fi
done

echo ""

# Check parent directory files
echo "Checking parent directory files..."
parent_files=(
    "../pyproject.toml"
    "../uv.lock"
    "../webinterfacemodule/app.py"
    "../Qwen_instructor_7B/manual_mode.py"
)

for file in "${parent_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $(basename $file)"
    else
        echo "  ❌ $(basename $file) (MISSING)"
        missing=1
    fi
done

echo ""

# Check Qwen model
echo "Checking Qwen2.5-VL-7B model..."
if [ -d "../Qwen_instructor_7B" ]; then
    model_size=$(du -sh ../Qwen_instructor_7B | cut -f1)
    echo "  ✅ Model found ($model_size)"
else
    echo "  ⚠️  Model not found at ../Qwen_instructor_7B"
    echo "     Model will be downloaded on first run"
fi

echo ""

# Check Docker
echo "Checking Docker installation..."
if command -v docker &> /dev/null; then
    docker_version=$(docker --version | cut -d' ' -f3 | tr -d ',')
    echo "  ✅ Docker $docker_version"
else
    echo "  ❌ Docker not found"
    missing=1
fi

if docker compose version &> /dev/null; then
    compose_version=$(docker compose version --short)
    echo "  ✅ docker compose $compose_version"
else
    echo "  ❌ docker compose not found"
    missing=1
fi

echo ""

# Check NVIDIA Docker runtime
echo "Checking NVIDIA Container Toolkit..."
if docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu24.04 nvidia-smi &> /dev/null; then
    echo "  ✅ NVIDIA runtime working"
else
    echo "  ❌ NVIDIA runtime not working"
    echo "     Install: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    missing=1
fi

echo ""
echo "================================================================================"

if [ $missing -eq 0 ]; then
    echo "✅ Validation PASSED - Ready to build!"
    echo ""
    echo "Next steps:"
    echo "  ./scripts/build.sh          # Build Docker image"
    echo "  ./scripts/start.sh          # Start service"
    echo "  docker compose up --build   # Build and start"
    echo ""
else
    echo "❌ Validation FAILED - Fix missing components"
    exit 1
fi
