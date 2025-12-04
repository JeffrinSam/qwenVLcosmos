# Cosmos Predict 2.5 + Qwen2.5-VL-7B - Complete Setup Guide

## Quick Start (VS Code Terminal)

### Prerequisites
- RTX 5090 GPU (CUDA 12.8 support)
- Ubuntu 22.04+
- Docker + NVIDIA Container Toolkit (for production)

### Local Development (VS Code Terminal)

```bash
# 1. Install Cosmos with CUDA support
cd /home/humanoid/Downloads/cosmos-predict2.5
uv sync --extra=cu128

# 2. Start web interface
cd webinterfacemodule
python3 app.py

# Access: http://localhost:5000
# Login: admin / cosmos2025
```

### Docker Production (Recommended)

```bash
# Build and run
cd /home/humanoid/Downloads/cosmos-predict2.5/Docker101
docker-compose up --build

# Access: http://localhost:5000
```

---

## Three Modes

| Mode | Use Case | Script |
|------|----------|--------|
| **Manual** | Full control, custom prompts | `manual_mode.py` |
| **Embodiment** | SO-1 arm / 2-wheel / UR3 robots | `prompt_extender_*.py` |
| **General** | Any robot/scene with AI analysis | `prompt_extender_general.py` |

---

## Command Line Usage

```bash
cd Qwen_instructor

# Manual mode (no AI)
python3 manual_mode.py \
  --image path/to/image.jpg \
  --prompt "Robot moves forward" \
  --frames 77 --resolution 768x432

# Embodiment mode (SO-1 arm with AI)
python3 prompt_extender_so1_arm.py \
  --image path/to/image.jpg \
  --prompt "pick up cube" \
  --output ../outputs/prompt.txt

# General mode (any robot with AI)
python3 prompt_extender_general.py \
  --image path/to/image.jpg \
  --prompt "navigate forward" \
  --output ../outputs/prompt.txt
```

---

## Web Interface Features

- 3-mode selection (Manual / Embodiment / General)
- Real-time generation status with colored console
- Extended prompt display (AI-generated details)
- Video preview and download
- Prompt/config download

---

## File Structure

```
cosmos-predict2.5/
├── Qwen_instructor_7B/          # AI prompt enhancement scripts
│   ├── manual_mode.py
│   ├── prompt_extender_so1_arm.py
│   ├── prompt_extender_2wheel_mobile.py
│   ├── prompt_extender_bimanual_ur3.py
│   └── prompt_extender_general.py
├── Qwen_instructor_7B/       # Qwen2.5-VL-7B model (15.6 GB)
├── webinterfacemodule/       # Flask web UI
│   ├── app.py
│   ├── templates/
│   ├── static/
│   ├── uploads/              # User images
│   └── outputs/              # Generated videos
└── Docker101/                # Production Docker setup
    ├── Dockerfile
    ├── docker-compose.yml
    └── config/
```

---

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'cosmos_cuda'`
**Fix**: Run `uv sync --extra=cu128` or use Docker

**Issue**: `jinja2.exceptions.UndefinedError`
**Fix**: Fixed in current version

**Issue**: `invalid literal for int()`
**Fix**: Fixed - now handles all resolution formats

---

## Production Deployment

See `Docker101/README.md` for production deployment with Docker.

**Security**: Change default password in `webinterfacemodule/app.py` line 21

---

## Support

- Official Docs: [docs/](docs/)
- Docker Setup: [Docker101/README.md](Docker101/README.md)
- Issues: Check console output for detailed errors
