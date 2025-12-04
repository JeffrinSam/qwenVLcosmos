# Complete Docker Commands Reference

**Cosmos Predict 2.5 - RTX 5090 Optimized**
**Last Updated**: December 4, 2025

---

## Table of Contents

1. [Setup & Installation](#setup--installation)
2. [Building & Deployment](#building--deployment)
3. [Container Management](#container-management)
4. [Monitoring & Debugging](#monitoring--debugging)
5. [GPU Operations](#gpu-operations)
6. [Backup & Restore](#backup--restore)
7. [Maintenance](#maintenance)
8. [Troubleshooting Commands](#troubleshooting-commands)
9. [Advanced Operations](#advanced-operations)
10. [Quick Reference](#quick-reference)

---

## Setup & Installation

### Install Docker

```bash
# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify installation
docker --version

# Add user to docker group (avoid sudo)
sudo usermod -aG docker $USER
newgrp docker

# Test Docker
docker run hello-world
```

### Install Docker Compose

```bash
# Install Docker Compose plugin
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verify installation
docker compose version
```

### Install NVIDIA Docker Runtime

```bash
# Add NVIDIA Docker repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install NVIDIA Container Toolkit
sudo apt-get update
sudo apt-get install -y nvidia-docker2

# Restart Docker daemon
sudo systemctl restart docker

# Test GPU access
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu24.04 nvidia-smi
```

### Download Models

```bash
# Navigate to project
cd /home/humanoid/Downloads/cosmos-predict2.5

# Download Qwen2.5-VL-7B model (~14GB)
python3 Qwen_instructor_7B/download_qwen_instructor.py

# Verify download
ls -lh Qwen_instructor_7B/*.safetensors

# Check total size
du -sh Qwen_instructor_7B/
```

### Validate Setup

```bash
# Run validation script
cd Docker101
chmod +x validate.sh
./validate.sh

# Check all prerequisites
# - Docker installed
# - Docker Compose installed
# - NVIDIA driver (565+)
# - NVIDIA Docker runtime
# - Required directories
# - Qwen model downloaded
# - Sufficient disk space (100GB+)
# - Sufficient RAM (32GB+)
```

---

## Building & Deployment

### Basic Build Commands

```bash
# Navigate to Docker directory
cd /home/humanoid/Downloads/cosmos-predict2.5/Docker101

# Enable BuildKit (faster builds)
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Build image (first time: 10-20 minutes)
docker compose build

# Build without cache (clean build)
docker compose build --no-cache

# Build specific stage
docker compose build --target app

# Build with progress output
docker compose build --progress=plain

# Build with verbose output
BUILDKIT_PROGRESS=plain docker compose build
```

### Advanced Build Options

```bash
# Build with build arguments
docker compose build --build-arg PYTHON_VERSION=3.10

# Build with specific Dockerfile
docker compose build -f Dockerfile.dev

# Build and start immediately
docker compose up --build -d

# Build with inline cache for CI/CD
docker compose build --build-arg BUILDKIT_INLINE_CACHE=1

# Build specific service (if multiple services)
docker compose build cosmos-web

# Build with memory limit
docker compose build --memory 16g
```

### Start & Deploy

```bash
# Start container in background (detached mode)
docker compose up -d

# Start with logs visible
docker compose up

# Start and rebuild if needed
docker compose up -d --build

# Start specific service
docker compose up -d cosmos-web

# Start with custom compose file
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Start and force recreate containers
docker compose up -d --force-recreate

# Start with specific timeout
docker compose up -d --timeout 120
```

### Stop & Remove

```bash
# Stop containers (keeps data)
docker compose stop

# Stop specific service
docker compose stop cosmos-web

# Stop with timeout
docker compose stop -t 30

# Stop and remove containers
docker compose down

# Stop and remove with volumes (WARNING: deletes data)
docker compose down -v

# Stop and remove with images
docker compose down --rmi all

# Force stop all containers
docker stop $(docker ps -aq)
```

---

## Container Management

### Status & Information

```bash
# Check container status
docker compose ps

# Check all containers (including stopped)
docker compose ps -a

# View container details
docker inspect cosmos-predict-web

# View container stats (CPU, memory, network)
docker stats cosmos-predict-web

# View container stats for all containers
docker stats

# Check container health
docker compose ps | grep healthy

# View container processes
docker top cosmos-predict-web

# View port mappings
docker port cosmos-predict-web
```

### Logs & Output

```bash
# View logs (follow mode - live updates)
docker compose logs -f cosmos-web

# View last 100 lines
docker compose logs --tail=100 cosmos-web

# View logs since specific time
docker compose logs --since 10m cosmos-web

# View logs with timestamps
docker compose logs -t cosmos-web

# View logs for all services
docker compose logs -f

# Save logs to file
docker compose logs > cosmos-logs-$(date +%Y%m%d).txt

# Search logs for errors
docker compose logs cosmos-web | grep -i error

# Search logs for specific pattern
docker compose logs cosmos-web | grep "CUDA"

# View logs in JSON format
docker logs cosmos-predict-web --format json
```

### Restart & Reload

```bash
# Restart container
docker compose restart cosmos-web

# Restart all services
docker compose restart

# Restart with timeout
docker compose restart -t 30 cosmos-web

# Force restart (stop and start)
docker compose stop cosmos-web && docker compose up -d cosmos-web

# Reload configuration (without recreating)
docker compose up -d --no-recreate

# Recreate container (new container, same config)
docker compose up -d --force-recreate cosmos-web
```

### Execute Commands in Container

```bash
# Enter container shell (interactive)
docker exec -it cosmos-predict-web bash

# Enter as root user
docker exec -it -u root cosmos-predict-web bash

# Run single command
docker exec cosmos-predict-web nvidia-smi

# Run command with output
docker exec cosmos-predict-web python3 --version

# Run command in specific directory
docker exec -w /workspace/webinterfacemodule cosmos-predict-web ls -la

# Run command with environment variable
docker exec -e DEBUG=1 cosmos-predict-web python3 test.py

# Copy file from container
docker cp cosmos-predict-web:/workspace/outputs/video.mp4 ./

# Copy file to container
docker cp ./config.json cosmos-predict-web:/workspace/

# Copy directory from container
docker cp cosmos-predict-web:/workspace/outputs/ ./outputs/
```

---

## Monitoring & Debugging

### Health Checks

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' cosmos-predict-web

# View health check history
docker inspect --format='{{json .State.Health}}' cosmos-predict-web | jq

# Manual health check
curl http://localhost:5000/health

# Check health endpoint with details
curl -v http://localhost:5000/health

# Check if container is running
docker ps | grep cosmos-predict-web

# View unhealthy containers
docker ps --filter health=unhealthy
```

### Resource Usage

```bash
# Real-time stats
docker stats cosmos-predict-web

# Stats in JSON format
docker stats --no-stream --format "{{json .}}" cosmos-predict-web

# Check disk usage
docker system df

# Detailed disk usage
docker system df -v

# Check specific container disk usage
docker exec cosmos-predict-web df -h

# Check container network usage
docker stats --no-stream --format "table {{.Name}}\t{{.NetIO}}"

# Check memory usage
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"

# Check CPU usage
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}"
```

### Network Debugging

```bash
# List networks
docker network ls

# Inspect network
docker network inspect cosmos-network

# Check container IP
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' cosmos-predict-web

# Test connectivity from host
ping $(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' cosmos-predict-web)

# Test connectivity from inside container
docker exec cosmos-predict-web ping google.com

# Check DNS resolution
docker exec cosmos-predict-web nslookup google.com

# View open ports
docker exec cosmos-predict-web netstat -tulpn

# Check port 5000
docker exec cosmos-predict-web netstat -tulpn | grep 5000
```

### Process Debugging

```bash
# View running processes in container
docker top cosmos-predict-web

# View all processes
docker exec cosmos-predict-web ps aux

# View Python processes
docker exec cosmos-predict-web ps aux | grep python

# View GPU processes
docker exec cosmos-predict-web fuser -v /dev/nvidia*

# Kill specific process
docker exec cosmos-predict-web kill -9 <PID>

# Check environment variables
docker exec cosmos-predict-web env

# Check specific environment variable
docker exec cosmos-predict-web echo $CUDA_VISIBLE_DEVICES
```

---

## GPU Operations

### GPU Status & Monitoring

```bash
# Check GPU from host
nvidia-smi

# Check GPU from container
docker exec cosmos-predict-web nvidia-smi

# Real-time GPU monitoring (host)
watch -n 1 nvidia-smi

# Real-time GPU monitoring (container)
docker exec cosmos-predict-web watch -n 1 nvidia-smi

# Detailed GPU info
docker exec cosmos-predict-web nvidia-smi -q

# GPU memory info
docker exec cosmos-predict-web nvidia-smi --query-gpu=memory.used,memory.free,memory.total --format=csv

# GPU utilization
docker exec cosmos-predict-web nvidia-smi --query-gpu=utilization.gpu,utilization.memory --format=csv

# GPU temperature
docker exec cosmos-predict-web nvidia-smi --query-gpu=temperature.gpu --format=csv

# GPU processes
docker exec cosmos-predict-web nvidia-smi pmon -s m -d 1

# GPU detailed monitoring
docker exec cosmos-predict-web nvidia-smi dmon -s pucvmet -d 1
```

### CUDA Operations

```bash
# Check CUDA version
docker exec cosmos-predict-web nvcc --version

# Check PyTorch CUDA
docker exec cosmos-predict-web python3 -c "import torch; print(torch.cuda.is_available())"

# Check PyTorch CUDA version
docker exec cosmos-predict-web python3 -c "import torch; print(torch.version.cuda)"

# Check GPU device count
docker exec cosmos-predict-web python3 -c "import torch; print(torch.cuda.device_count())"

# Check GPU device name
docker exec cosmos-predict-web python3 -c "import torch; print(torch.cuda.get_device_name(0))"

# Check CUDA memory
docker exec cosmos-predict-web python3 -c "import torch; print(f'Allocated: {torch.cuda.memory_allocated(0)/1024**3:.2f}GB')"

# Clear CUDA cache
docker exec cosmos-predict-web python3 -c "import torch; torch.cuda.empty_cache()"

# Check cuDNN version
docker exec cosmos-predict-web python3 -c "import torch; print(torch.backends.cudnn.version())"

# Test GPU computation
docker exec cosmos-predict-web python3 -c "import torch; x = torch.rand(1000, 1000).cuda(); print('GPU test passed')"
```

### GPU Memory Management

```bash
# Check memory stats
docker exec cosmos-predict-web python3 -c "
import torch
print(f'Allocated: {torch.cuda.memory_allocated(0)/1024**3:.2f}GB')
print(f'Reserved: {torch.cuda.memory_reserved(0)/1024**3:.2f}GB')
print(f'Max allocated: {torch.cuda.max_memory_allocated(0)/1024**3:.2f}GB')
"

# Clear cache and check memory
docker exec cosmos-predict-web python3 -c "
import torch
torch.cuda.empty_cache()
torch.cuda.reset_peak_memory_stats()
print('CUDA cache cleared')
"

# Check memory summary
docker exec cosmos-predict-web python3 -c "
import torch
print(torch.cuda.memory_summary(device=0, abbreviated=False))
"

# Monitor memory during operation
docker exec cosmos-predict-web python3 -c "
import torch, time
for i in range(10):
    print(f'Allocated: {torch.cuda.memory_allocated(0)/1024**3:.2f}GB')
    time.sleep(1)
"
```

---

## Backup & Restore

### Backup Data

```bash
# Backup uploads directory
tar -czf cosmos-uploads-$(date +%Y%m%d).tar.gz \
  /home/humanoid/Downloads/cosmos-predict2.5/webinterfacemodule/uploads/

# Backup outputs directory
tar -czf cosmos-outputs-$(date +%Y%m%d).tar.gz \
  /home/humanoid/Downloads/cosmos-predict2.5/webinterfacemodule/outputs/

# Backup both uploads and outputs
tar -czf cosmos-data-$(date +%Y%m%d).tar.gz \
  /home/humanoid/Downloads/cosmos-predict2.5/webinterfacemodule/uploads/ \
  /home/humanoid/Downloads/cosmos-predict2.5/webinterfacemodule/outputs/

# Backup Docker volumes
docker run --rm \
  -v cosmos-web_huggingface-cache:/data \
  -v $(pwd):/backup \
  alpine \
  tar czf /backup/hf-cache-$(date +%Y%m%d).tar.gz /data

# Backup container
docker commit cosmos-predict-web cosmos-predict2.5:backup-$(date +%Y%m%d)

# Export container as tar
docker save cosmos-predict2.5:latest > cosmos-predict2.5-$(date +%Y%m%d).tar

# Backup logs
docker compose logs > cosmos-logs-$(date +%Y%m%d).txt

# Automated backup script
cat << 'EOF' > backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/cosmos"
mkdir -p $BACKUP_DIR

tar -czf $BACKUP_DIR/uploads-$DATE.tar.gz webinterfacemodule/uploads/
tar -czf $BACKUP_DIR/outputs-$DATE.tar.gz webinterfacemodule/outputs/
docker compose logs > $BACKUP_DIR/logs-$DATE.txt

echo "Backup completed: $DATE"
EOF
chmod +x backup.sh
```

### Restore Data

```bash
# Restore uploads
tar -xzf cosmos-uploads-20251204.tar.gz -C /home/humanoid/Downloads/cosmos-predict2.5/webinterfacemodule/

# Restore outputs
tar -xzf cosmos-outputs-20251204.tar.gz -C /home/humanoid/Downloads/cosmos-predict2.5/webinterfacemodule/

# Restore Docker volume
docker run --rm \
  -v cosmos-web_huggingface-cache:/data \
  -v $(pwd):/backup \
  alpine \
  sh -c "cd /data && tar xzf /backup/hf-cache-20251204.tar.gz --strip 1"

# Load saved image
docker load < cosmos-predict2.5-20251204.tar

# Import container backup
docker import cosmos-backup.tar cosmos-predict2.5:restored

# Restore specific files from container backup
docker run --rm cosmos-predict2.5:backup-20251204 cat /workspace/config.json > config.json
```

---

## Maintenance

### Clean Up

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune

# Remove all unused data (containers, images, networks, volumes)
docker system prune -a --volumes

# Clean build cache
docker builder prune

# Clean all build cache
docker builder prune -af

# Remove specific image
docker rmi cosmos-predict2.5:latest

# Remove specific volume
docker volume rm cosmos-web_huggingface-cache

# Remove dangling images
docker image prune -f

# Check what will be removed (dry run)
docker system prune --dry-run
```

### Update Operations

```bash
# Update base image
docker pull nvidia/cuda:12.8.1-cudnn9-devel-ubuntu24.04

# Update Cosmos code
cd /home/humanoid/Downloads/cosmos-predict2.5
git pull
uv sync --extra cu128

# Rebuild image
cd Docker101
docker compose build --no-cache

# Restart with new image
docker compose down
docker compose up -d

# Update and restart (one command)
cd /home/humanoid/Downloads/cosmos-predict2.5 && \
git pull && \
cd Docker101 && \
docker compose build && \
docker compose up -d
```

### Log Management

```bash
# View log file location
docker inspect --format='{{.LogPath}}' cosmos-predict-web

# Check log file size
docker inspect --format='{{.LogPath}}' cosmos-predict-web | xargs ls -lh

# Clear logs (truncate)
truncate -s 0 $(docker inspect --format='{{.LogPath}}' cosmos-predict-web)

# Archive logs
docker compose logs > cosmos-logs-archive-$(date +%Y%m%d).txt
truncate -s 0 $(docker inspect --format='{{.LogPath}}' cosmos-predict-web)

# Rotate logs manually
docker compose logs > /var/log/cosmos/cosmos-$(date +%Y%m%d).log
gzip /var/log/cosmos/cosmos-$(date +%Y%m%d).log

# Configure log rotation (in docker-compose.yml)
# Already configured:
# logging:
#   driver: "json-file"
#   options:
#     max-size: "100m"
#     max-file: "3"
```

---

## Troubleshooting Commands

### Debug Container Issues

```bash
# Check if container exists
docker ps -a | grep cosmos-predict-web

# Check container exit code
docker inspect cosmos-predict-web --format='{{.State.ExitCode}}'

# Check why container stopped
docker inspect cosmos-predict-web --format='{{.State.Status}}: {{.State.Error}}'

# View last 50 log lines
docker compose logs --tail=50 cosmos-web

# Check for errors in logs
docker compose logs cosmos-web | grep -i error

# Check for OOM errors
docker compose logs cosmos-web | grep -i "out of memory"

# Check container startup time
docker inspect cosmos-predict-web --format='{{.State.StartedAt}}'

# Check container configuration
docker inspect cosmos-predict-web | jq '.[0].Config'

# Validate docker-compose.yml
docker compose config

# Check compose file syntax
docker compose -f docker-compose.yml config --quiet
```

### Network Troubleshooting

```bash
# Check if port is listening
netstat -tulpn | grep 5000

# Check if port is blocked by firewall
sudo ufw status | grep 5000

# Find process using port
sudo lsof -i :5000

# Test connection to container
curl -v http://localhost:5000

# Test connection from inside container
docker exec cosmos-predict-web curl -v http://localhost:5000

# Check DNS resolution
docker exec cosmos-predict-web nslookup google.com

# Test internet connectivity
docker exec cosmos-predict-web ping -c 4 8.8.8.8

# Check routing
docker exec cosmos-predict-web traceroute google.com

# View iptables rules
sudo iptables -L -n | grep 5000
```

### Permission Issues

```bash
# Check file permissions
docker exec cosmos-predict-web ls -la /workspace/webinterfacemodule/uploads

# Fix permissions from host
chmod -R 777 /home/humanoid/Downloads/cosmos-predict2.5/webinterfacemodule/uploads
chmod -R 777 /home/humanoid/Downloads/cosmos-predict2.5/webinterfacemodule/outputs

# Fix permissions from container (as root)
docker exec -u root cosmos-predict-web chown -R 1000:1000 /workspace/webinterfacemodule/uploads
docker exec -u root cosmos-predict-web chown -R 1000:1000 /workspace/webinterfacemodule/outputs

# Check user inside container
docker exec cosmos-predict-web whoami
docker exec cosmos-predict-web id

# Run command as root
docker exec -u root cosmos-predict-web bash
```

### GPU Troubleshooting

```bash
# Test GPU access from host
nvidia-smi

# Test GPU access from container
docker exec cosmos-predict-web nvidia-smi

# Check NVIDIA Docker runtime
docker run --rm --gpus all nvidia/cuda:12.8.1-base-ubuntu24.04 nvidia-smi

# Check GPU driver version
nvidia-smi --query-gpu=driver_version --format=csv,noheader

# Check if GPU is visible to container
docker exec cosmos-predict-web ls -la /dev/nvidia*

# Check CUDA environment variables
docker exec cosmos-predict-web env | grep CUDA

# Test PyTorch GPU
docker exec cosmos-predict-web python3 -c "import torch; print('CUDA available:', torch.cuda.is_available())"

# Check GPU memory errors
docker compose logs cosmos-web | grep -i "out of memory"

# Monitor GPU during operation
watch -n 1 'nvidia-smi; echo "---"; docker exec cosmos-predict-web nvidia-smi'
```

---

## Advanced Operations

### Multi-Container Operations

```bash
# Start multiple compose files
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale service (if configured)
docker compose up -d --scale cosmos-web=3

# Run command in all containers
docker ps -q | xargs -I {} docker exec {} nvidia-smi

# Stop all containers
docker stop $(docker ps -q)

# Remove all containers
docker rm $(docker ps -aq)

# Remove all images
docker rmi $(docker images -q)
```

### Performance Tuning

```bash
# Set CPU limit
docker update --cpus="8" cosmos-predict-web

# Set memory limit
docker update --memory="32g" cosmos-predict-web

# Set CPU shares (priority)
docker update --cpu-shares=1024 cosmos-predict-web

# View resource limits
docker inspect cosmos-predict-web --format='{{.HostConfig.Memory}}'

# Run with specific CPU cores
docker run --cpuset-cpus="0-7" ...

# Run with memory limit
docker run --memory="32g" --memory-swap="64g" ...
```

### Image Operations

```bash
# List images
docker images

# List images with digests
docker images --digests

# Tag image
docker tag cosmos-predict2.5:latest cosmos-predict2.5:v1.0

# Push to registry
docker push your-registry/cosmos-predict2.5:latest

# Pull from registry
docker pull your-registry/cosmos-predict2.5:latest

# Inspect image layers
docker history cosmos-predict2.5:latest

# View image size by layer
docker history cosmos-predict2.5:latest --human --no-trunc

# Export image
docker save cosmos-predict2.5:latest | gzip > cosmos-predict2.5.tar.gz

# Import image
gunzip -c cosmos-predict2.5.tar.gz | docker load
```

### Volume Operations

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect cosmos-web_huggingface-cache

# Create volume
docker volume create my-volume

# Remove volume
docker volume rm my-volume

# Copy files from volume
docker run --rm -v cosmos-web_huggingface-cache:/data -v $(pwd):/backup alpine cp /data/file.txt /backup/

# Backup volume
docker run --rm -v cosmos-web_huggingface-cache:/data -v $(pwd):/backup alpine tar czf /backup/volume-backup.tar.gz /data

# View volume size
docker system df -v | grep cosmos-web
```

---

## Quick Reference

### Most Common Commands

```bash
# Validate setup
cd /home/humanoid/Downloads/cosmos-predict2.5/Docker101 && ./validate.sh

# Build
docker compose build

# Start
docker compose up -d

# Stop
docker compose down

# View logs
docker compose logs -f cosmos-web

# Restart
docker compose restart cosmos-web

# Enter container
docker exec -it cosmos-predict-web bash

# Check GPU
docker exec cosmos-predict-web nvidia-smi

# Clear CUDA cache
docker exec cosmos-predict-web python3 -c "import torch; torch.cuda.empty_cache()"

# Check status
docker compose ps

# View stats
docker stats cosmos-predict-web
```

### One-Liners

```bash
# Complete rebuild
docker compose down && docker compose build --no-cache && docker compose up -d

# Update and restart
cd .. && git pull && cd Docker101 && docker compose build && docker compose up -d

# Clean and restart
docker compose down && docker system prune -af && docker compose up -d --build

# Backup everything
tar -czf cosmos-backup-$(date +%Y%m%d).tar.gz webinterfacemodule/uploads/ webinterfacemodule/outputs/

# Check all resources
docker stats --no-stream && nvidia-smi && df -h

# Full health check
docker compose ps && curl http://localhost:5000/health && docker exec cosmos-predict-web nvidia-smi
```

### Aliases (Add to ~/.bashrc)

```bash
# Add these to ~/.bashrc for quick access
alias dc='docker compose'
alias dps='docker compose ps'
alias dup='docker compose up -d'
alias ddown='docker compose down'
alias dlog='docker compose logs -f'
alias dbuild='docker compose build'
alias drestart='docker compose restart'
alias dexec='docker exec -it cosmos-predict-web bash'
alias dgpu='docker exec cosmos-predict-web nvidia-smi'
alias dstats='docker stats cosmos-predict-web'

# Reload bashrc
source ~/.bashrc

# Usage:
# dc ps
# dup
# dlog cosmos-web
```

---

## Command Cheat Sheet by Task

### Task: First Time Setup
```bash
cd /home/humanoid/Downloads/cosmos-predict2.5/Docker101
./validate.sh
docker compose build
docker compose up -d
docker compose logs -f cosmos-web
# Open http://localhost:5000
```

### Task: Daily Start/Stop
```bash
docker compose up -d      # Start
docker compose down       # Stop
docker compose restart    # Restart
```

### Task: Check if Working
```bash
docker compose ps
curl http://localhost:5000/health
docker exec cosmos-predict-web nvidia-smi
```

### Task: View Logs for Errors
```bash
docker compose logs --tail=100 cosmos-web | grep -i error
docker compose logs -f cosmos-web
```

### Task: Out of Memory Error
```bash
docker compose restart cosmos-web
docker exec cosmos-predict-web python3 -c "import torch; torch.cuda.empty_cache()"
nvidia-smi
```

### Task: Update Code
```bash
cd /home/humanoid/Downloads/cosmos-predict2.5
git pull
cd Docker101
docker compose build
docker compose up -d
```

### Task: Complete Reset
```bash
docker compose down -v
docker system prune -af
docker compose build --no-cache
docker compose up -d
```

---

**Document Version**: 1.0
**Last Updated**: December 4, 2025
**For**: Cosmos Predict 2.5 Docker Deployment

---

**Quick Access**:
- Full Guide: [README.md](README.md)
- Deployment Summary: [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)
- Optimization Details: [OPTIMIZATION_SUMMARY.md](OPTIMIZATION_SUMMARY.md)
