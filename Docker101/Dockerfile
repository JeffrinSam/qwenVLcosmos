# Production Docker for Cosmos Predict 2.5 + Web Interface
# Optimized for RTX 5090 (32GB VRAM) with CUDA 12.8
# Multi-stage build for optimal image size and layer caching

# =============================================================================
# Stage 1: Base image with CUDA development tools
# =============================================================================
FROM nvidia/cuda:12.8.1-cudnn9-devel-ubuntu24.04 AS base

# Metadata
LABEL maintainer="Cosmos Predict 2.5 Web Interface"
LABEL description="Production-ready Cosmos video generation with Qwen2.5-VL-7B"
LABEL gpu="NVIDIA RTX 5090"
LABEL cuda.version="12.8"

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CUDA_HOME=/usr/local/cuda \
    PATH="${CUDA_HOME}/bin:${PATH}" \
    LD_LIBRARY_PATH="${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}" \
    # PyTorch memory optimization for RTX 5090 (32GB VRAM)
    PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True,max_split_size_mb:512" \
    CUDA_LAUNCH_BLOCKING=0 \
    TORCH_CUDNN_V8_API_ENABLED=1 \
    # Hugging Face cache locations (can be mounted as volumes)
    HF_HOME=/workspace/.cache/huggingface \
    TRANSFORMERS_CACHE=/workspace/.cache/huggingface/transformers \
    HF_DATASETS_CACHE=/workspace/.cache/huggingface/datasets \
    # Reduce memory fragmentation
    MALLOC_TRIM_THRESHOLD_=100000

WORKDIR /workspace

# =============================================================================
# Stage 2: System dependencies
# =============================================================================
FROM base AS system-deps

RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core utilities
    curl \
    wget \
    ca-certificates \
    git \
    # Python dependencies
    python3.10 \
    python3.10-dev \
    python3.10-venv \
    python3-pip \
    # Build tools (required for PyTorch extensions)
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    # Media processing
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    # Utilities
    tree \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# =============================================================================
# Stage 3: Python environment setup with UV
# =============================================================================
FROM system-deps AS python-env

# Install UV package manager (faster than pip)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Upgrade pip and install core build tools
RUN python3 -m pip install --no-cache-dir --upgrade \
    pip==24.3.1 \
    setuptools==75.6.0 \
    wheel==0.45.1

# =============================================================================
# Stage 4: Dependencies installation
# =============================================================================
FROM python-env AS deps

# Copy only dependency files first (for layer caching)
COPY pyproject.toml uv.lock ./
COPY packages ./packages

# Install Cosmos Predict with CUDA 12.8 support using UV
# This installs torch with proper CUDA 12.8 binaries
RUN uv sync --frozen --extra cu128 --no-dev

# Install web interface requirements
COPY webinterfacemodule/requirements.txt /tmp/web-requirements.txt
RUN uv pip install --no-cache-dir -r /tmp/web-requirements.txt

# Install additional dependencies for Qwen VL
RUN uv pip install --no-cache-dir \
    qwen-vl-utils \
    accelerate \
    bitsandbytes \
    peft \
    pillow

# =============================================================================
# Stage 5: Application code
# =============================================================================
FROM deps AS app

# Copy application code
COPY cosmos_predict2 ./cosmos_predict2
COPY examples ./examples
COPY bin ./bin
COPY Qwen_instructor_7B ./Qwen_instructor_7B
COPY webinterfacemodule ./webinterfacemodule
COPY assets ./assets

# Install Cosmos Predict in editable mode
RUN uv pip install --no-cache-dir -e .

# Create necessary directories with proper permissions
RUN mkdir -p \
    /workspace/webinterfacemodule/uploads \
    /workspace/webinterfacemodule/outputs \
    /workspace/.cache/huggingface \
    /workspace/Qwen_instructor_7B \
    /workspace/Inputimg \
    && chmod -R 777 /workspace/webinterfacemodule/uploads \
    && chmod -R 777 /workspace/webinterfacemodule/outputs \
    && chmod -R 777 /workspace/.cache

# =============================================================================
# Stage 6: Production runtime
# =============================================================================
FROM app AS runtime

# Health check for web interface
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose web interface port
EXPOSE 5000

# Create startup script for memory-optimized launch
RUN echo '#!/bin/bash\n\
set -e\n\
echo "=== Cosmos Predict 2.5 Docker Container ==="\n\
echo "CUDA Version: $(nvcc --version | grep release)"\n\
echo "GPU Info: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader)"\n\
echo "PyTorch Memory Config: $PYTORCH_CUDA_ALLOC_CONF"\n\
echo "=========================================="\n\
# Clear CUDA cache before starting\n\
python3 -c "import torch; torch.cuda.empty_cache()" 2>/dev/null || true\n\
# Start web interface\n\
exec python3 webinterfacemodule/app.py\n\
' > /workspace/start.sh && chmod +x /workspace/start.sh

# Default command: Start web interface with memory optimizations
CMD ["/workspace/start.sh"]
