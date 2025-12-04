# Cosmos Predict 2.5 Docker Deployment Guide

Production-ready Docker setup for NVIDIA Cosmos Predict 2.5 with Qwen2.5-VL-7B, optimized for RTX 5090 (32GB VRAM).

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Memory Optimization](#memory-optimization)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)
8. [Performance Tuning](#performance-tuning)

---

## Overview

This Docker setup provides:

- **Multi-stage build** for optimal image size and build caching
- **RTX 5090 optimizations** with CUDA 12.8 and cuDNN 9
- **Memory management** to prevent CUDA OOM errors
- **Production-ready** with health checks, logging, and security
- **Persistent storage** for models, uploads, and outputs
- **UV package manager** for fast dependency installation

### Architecture

```
┌─────────────────────────────────────────────┐
│  Web Interface (Flask)                      │
│  http://localhost:5000                      │
├─────────────────────────────────────────────┤
│  Qwen2.5-VL-7B (Prompt Enhancement)         │
│  + Cosmos Predict 2.5 (Video Generation)    │
├─────────────────────────────────────────────┤
│  CUDA 12.8 + cuDNN 9 + PyTorch 2.7          │
├─────────────────────────────────────────────┤
│  NVIDIA RTX 5090 (32GB VRAM)                │
└─────────────────────────────────────────────┘
```

---

## Prerequisites

### System Requirements

- **GPU**: NVIDIA RTX 5090 (32GB VRAM) or equivalent
- **CPU**: 8+ cores recommended
- **RAM**: 64GB system memory recommended
- **Storage**: 100GB+ free space
- **OS**: Linux with kernel 5.15+ (Ubuntu 24.04 recommended)

### Software Requirements

1. **Docker Engine** (24.0+):
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

2. **Docker Compose** (2.20+):
   ```bash
   sudo apt-get update
   sudo apt-get install docker-compose-plugin
   ```

3. **NVIDIA Docker Runtime**:
   ```bash
   # Add NVIDIA Docker repository
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
     sudo tee /etc/apt/sources.list.d/nvidia-docker.list

   # Install NVIDIA Container Toolkit
   sudo apt-get update
   sudo apt-get install -y nvidia-docker2
   sudo systemctl restart docker
   ```

4. **NVIDIA Driver** (565+):
   ```bash
   # Verify driver installation
   nvidia-smi
   ```

### Verify Installation

```bash
# Test NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu24.04 nvidia-smi
```

---

## Quick Start

### 1. Prepare Models

Download the Qwen2.5-VL-7B model (required):

```bash
cd /home/humanoid/Downloads/cosmos-predict2.5
python3 Qwen_instructor_7B/download_qwen_instructor.py
```

This downloads ~14GB to `Qwen_instructor_7B/` directory.

### 2. Build Docker Image

```bash
cd Docker101

# Build the image (takes 10-20 minutes first time)
docker compose build

# Or build with specific target stage
docker compose build --build-arg BUILDKIT_INLINE_CACHE=1
```

### 3. Start the Container

```bash
# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f cosmos-web
```

### 4. Access Web Interface

Open browser to: [http://localhost:5000](http://localhost:5000)

### 5. Stop the Container

```bash
docker compose down
```

---

## Configuration

### Environment Variables

Key environment variables in `docker-compose.yml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `PYTORCH_CUDA_ALLOC_CONF` | PyTorch memory allocator | `expandable_segments:True,max_split_size_mb:512` |
| `CUDA_VISIBLE_DEVICES` | GPU selection | `0` |
| `HF_HOME` | Hugging Face cache | `/workspace/.cache/huggingface` |
| `FLASK_ENV` | Flask environment | `production` |

### Volume Mounts

The compose file mounts these directories:

```yaml
volumes:
  # Models (read-only)
  - ../Qwen_instructor_7B:/workspace/Qwen_instructor_7B:ro
  - ../assets:/workspace/assets:ro

  # Data (read-write)
  - ../Inputimg:/workspace/Inputimg:rw
  - ../webinterfacemodule/uploads:/workspace/webinterfacemodule/uploads:rw
  - ../webinterfacemodule/outputs:/workspace/webinterfacemodule/outputs:rw

  # Caches (persistent volumes)
  - huggingface-cache:/workspace/.cache/huggingface
  - torch-cache:/workspace/.cache/torch
```

### Resource Limits

Adjust CPU/memory limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '16'      # Max CPU cores
      memory: 64G     # Max system RAM
    reservations:
      cpus: '8'       # Min CPU cores
      memory: 32G     # Min system RAM
```

---

## Memory Optimization

### Understanding Memory Usage

Cosmos Predict 2.5 loads multiple large models:

1. **Qwen2.5-VL-7B**: ~14GB VRAM
2. **Cosmos-Predict2.5-2B**: ~8GB VRAM
3. **Cosmos-Reason1-7B**: ~14GB VRAM
4. **VAE Tokenizer**: ~2GB VRAM

**Total**: ~38GB VRAM (exceeds RTX 5090's 32GB!)

### Memory Optimization Strategies

#### 1. PyTorch Memory Allocator

The Dockerfile sets:
```bash
PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True,max_split_size_mb:512"
```

- `expandable_segments:True` - reduces fragmentation
- `max_split_size_mb:512` - limits allocation chunk size

#### 2. Model Offloading

Edit `webinterfacemodule/app.py` to enable CPU offloading:

```python
# Load models with CPU offload
model = load_model(
    device_map="auto",           # Automatic device mapping
    low_cpu_mem_usage=True,      # Reduce CPU memory
    max_memory={0: "28GB", "cpu": "32GB"}  # Reserve VRAM
)
```

#### 3. 8-bit Quantization

Reduce VRAM by using 8-bit models:

```python
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0
)

model = load_model(quantization_config=quantization_config)
```

This reduces Qwen2.5-VL from 14GB → ~7GB.

#### 4. Shared Memory

The compose file sets:
```yaml
shm_size: '16gb'
```

Critical for PyTorch DataLoader. Increase if you see:
```
ERROR: Unexpected bus error encountered in worker
```

### Monitoring Memory

#### Inside Container

```bash
# Enter container
docker exec -it cosmos-predict-web bash

# Check GPU memory
nvidia-smi

# Monitor GPU usage
watch -n 1 nvidia-smi
```

#### Python Script

```python
import torch

# Check VRAM usage
print(f"Allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
print(f"Cached: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
print(f"Max allocated: {torch.cuda.max_memory_allocated(0) / 1024**3:.2f} GB")

# Clear cache
torch.cuda.empty_cache()
```

---

## Troubleshooting

### CUDA Out of Memory

**Error:**
```
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 130.00 MiB.
```

**Solutions:**

1. **Clear CUDA cache:**
   ```bash
   docker exec cosmos-predict-web python3 -c "import torch; torch.cuda.empty_cache()"
   ```

2. **Reduce batch size** in generation config:
   ```json
   {
     "video_generation": {
       "batch_size": 1,  // Reduce from default
       "num_frames": 20  // Reduce from 121
     }
   }
   ```

3. **Enable 8-bit quantization** (see [Memory Optimization](#memory-optimization))

4. **Use gradient checkpointing:**
   ```python
   model.gradient_checkpointing_enable()
   ```

### Model Download Fails

**Error:**
```
❌ Error: Failed to load model: No such file or directory
```

**Solution:**

```bash
# Download Qwen model manually
cd /home/humanoid/Downloads/cosmos-predict2.5
python3 Qwen_instructor_7B/download_qwen_instructor.py

# Verify download
ls -lh Qwen_instructor_7B/
```

### Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied: '/workspace/webinterfacemodule/uploads'
```

**Solution:**

```bash
# Fix permissions on host
chmod -R 777 webinterfacemodule/uploads
chmod -R 777 webinterfacemodule/outputs

# Or rebuild with correct permissions
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Docker Build Fails

**Error:**
```
ERROR: failed to solve: process "/bin/sh -c uv sync" did not complete successfully
```

**Solutions:**

1. **Check disk space:**
   ```bash
   df -h
   ```

2. **Clean Docker cache:**
   ```bash
   docker system prune -a --volumes
   ```

3. **Build with more memory:**
   ```bash
   docker compose build --memory 16g
   ```

### Health Check Failing

**Error:**
```
unhealthy: Health check failed
```

**Check logs:**

```bash
docker compose logs cosmos-web | grep health
```

**Solution:**

1. **Increase start period** in `docker-compose.yml`:
   ```yaml
   healthcheck:
     start_period: 180s  # Increase from 120s
   ```

2. **Check Flask app is running:**
   ```bash
   docker exec cosmos-predict-web curl http://localhost:5000/health
   ```

---

## Advanced Usage

### Multi-GPU Support

To use multiple GPUs:

```yaml
# docker-compose.yml
environment:
  - CUDA_VISIBLE_DEVICES=0,1  # Use GPU 0 and 1

deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['0', '1']
          capabilities: [gpu]
```

### Custom Network Configuration

For production deployments with reverse proxy:

```yaml
services:
  cosmos-web:
    networks:
      - backend
    expose:
      - "5000"  # Internal only

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    networks:
      - backend
      - frontend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true
```

### Persistent Logs

Mount log directory:

```yaml
volumes:
  - ./logs:/var/log/cosmos:rw
```

Configure logging in Flask app:

```python
import logging
logging.basicConfig(
    filename='/var/log/cosmos/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Development Mode

For development with live code reload:

```yaml
# docker-compose.dev.yml
services:
  cosmos-web:
    build:
      target: app  # Stop at app stage
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    volumes:
      - ../cosmos_predict2:/workspace/cosmos_predict2:rw  # Live reload
      - ../webinterfacemodule:/workspace/webinterfacemodule:rw
    command: python3 -m flask run --host=0.0.0.0 --port=5000 --reload
```

Start with:
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

## Performance Tuning

### Build Performance

1. **Enable BuildKit:**
   ```bash
   export DOCKER_BUILDKIT=1
   export COMPOSE_DOCKER_CLI_BUILD=1
   ```

2. **Use build cache:**
   ```bash
   docker compose build --build-arg BUILDKIT_INLINE_CACHE=1
   ```

3. **Parallel builds:**
   ```bash
   docker compose build --parallel
   ```

### Runtime Performance

1. **Disable CUDA launch blocking** (already set):
   ```bash
   CUDA_LAUNCH_BLOCKING=0
   ```

2. **Enable cuDNN auto-tuner:**
   ```python
   torch.backends.cudnn.benchmark = True
   ```

3. **Optimize DataLoader:**
   ```python
   DataLoader(
       dataset,
       batch_size=1,
       num_workers=4,          # Parallel loading
       pin_memory=True,        # Faster CPU→GPU transfer
       persistent_workers=True # Keep workers alive
   )
   ```

### Network Performance

For high-throughput scenarios:

```yaml
services:
  cosmos-web:
    network_mode: "host"  # Use host networking
```

**Note:** This removes network isolation but provides ~10% better performance.

---

## Maintenance

### Update Models

```bash
# Stop container
docker compose down

# Update Cosmos Predict
cd /home/humanoid/Downloads/cosmos-predict2.5
git pull
uv sync --extra cu128

# Rebuild image
cd Docker101
docker compose build
docker compose up -d
```

### Clear Caches

```bash
# Clear Hugging Face cache
docker volume rm docker101_huggingface-cache

# Clear PyTorch cache
docker volume rm docker101_torch-cache

# Recreate volumes
docker compose up -d
```

### Backup Data

```bash
# Backup outputs
tar -czf cosmos-outputs-$(date +%Y%m%d).tar.gz \
  webinterfacemodule/outputs/

# Backup uploads
tar -czf cosmos-uploads-$(date +%Y%m%d).tar.gz \
  webinterfacemodule/uploads/
```

---

## Security Considerations

### Production Deployment

1. **Use secrets for API keys:**
   ```yaml
   secrets:
     hf_token:
       file: ./secrets/hf_token.txt

   services:
     cosmos-web:
       secrets:
         - hf_token
   ```

2. **Enable firewall:**
   ```bash
   sudo ufw allow 5000/tcp
   sudo ufw enable
   ```

3. **Run as non-root user:**
   ```dockerfile
   # Add to Dockerfile
   RUN useradd -m -u 1000 cosmos
   USER cosmos
   ```

4. **Use HTTPS with certificates:**
   ```yaml
   services:
     cosmos-web:
       environment:
         - FLASK_RUN_CERT=/certs/cert.pem
         - FLASK_RUN_KEY=/certs/key.pem
   ```

---

## Additional Resources

### Documentation

- [NVIDIA Cosmos Documentation](https://docs.nvidia.com/cosmos/)
- [Docker NVIDIA Runtime](https://github.com/NVIDIA/nvidia-docker)
- [PyTorch CUDA Memory Management](https://pytorch.org/docs/stable/notes/cuda.html)

### Related Files

- [Dockerfile](Dockerfile) - Multi-stage Docker build
- [docker-compose.yml](docker-compose.yml) - Production compose config
- [../ALLMODES.md](../ALLMODES.md) - Complete user guide
- [../PROMPT_UPDATES_SUMMARY.md](../PROMPT_UPDATES_SUMMARY.md) - Prompt system updates

---

## License

Apache 2.0 - See [LICENSE](../LICENSE) for details.

---

## Support

For issues related to:
- **Docker setup**: Open issue in this repository
- **Cosmos Predict**: Check [NVIDIA Cosmos GitHub](https://github.com/nvidia-cosmos/cosmos-predict2.5)
- **Memory errors**: See [Troubleshooting](#troubleshooting) section above

---

**Last Updated**: December 4, 2025
**Docker Version**: 24.0+
**Compose Version**: 2.20+
**CUDA Version**: 12.8
