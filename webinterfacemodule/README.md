# Cosmos Predict 2.5 Web Interface

**Production-ready web interface for generating physics-based robotics videos.**

Combines Qwen2.5-VL-7B vision AI with Cosmos Predict 2.5 for automated video generation.

---

## Quick Start

```bash
cd /home/humanoid/Downloads/cosmos-predict2.5/webinterfacemodule
./START_HERE.sh
```

Then open: **http://localhost:5000**

---

## Features

- **4 Validated Robot Modes**
  - 🦾 SO-1 Arm (LeRobot) - Single-arm manipulation
  - 🤖 2-Wheel Mobile Robot - Navigation and movement
  - 🤝 Bimanual UR3 - Dual-arm coordination
  - 🔬 General Analyzer - Any robot or scene

- **Automated Pipeline**
  - Upload image → AI analysis → Enhanced prompt → Video generation
  - ~2-3 minutes per video (77 frames)

- **Modern Web UI**
  - Drag & drop image upload
  - Real-time status tracking
  - Video preview and download
  - Console output monitoring

- **Network Access**
  - Local and WiFi access supported
  - Optional authentication

---

## Documentation

📖 **[QUICK_START.md](QUICK_START.md)** - User-friendly guide to get started

🔧 **[UPDATES.md](UPDATES.md)** - Recent changes and technical details

📚 **[../ALLMODES.md](../ALLMODES.md)** - Comprehensive documentation covering all interfaces and modes

---

## What's New (Dec 3, 2025)

✅ **Critical Fix**: Added `--disable-guardrails` flag - robotics prompts work perfectly!

✅ **Updated Model**: Using Qwen2.5-VL-7B (16GB model) for better analysis

✅ **Validated**: All 4 modes tested with successful video generation

✅ **Improved**: Automatic startup script with port cleanup

---

## Requirements

- **GPU**: CUDA-enabled, 32GB VRAM recommended
- **Python**: 3.10+ with virtual environment at `../.venv/`
- **Dependencies**: Installed automatically via `START_HERE.sh`

---

## Basic Usage

1. **Start Server**: `./START_HERE.sh`
2. **Open Browser**: http://localhost:5000
3. **Select Mode**: Choose robot type
4. **Upload Image**: Drag & drop your robot image
5. **Enter Prompt**: Describe the task (e.g., "pick and place bottle")
6. **Generate**: Click button and wait ~2-3 minutes
7. **Download**: Get video and enhanced prompt

---

## Example Workflows

### SO-1 Arm Video
```bash
Upload: Inputimg/so1/1.jpg
Prompt: "pick and place the bottle"
Mode: SO-1 Arm (LeRobot)
Result: 77-frame manipulation video
```

### Mobile Robot Video
```bash
Upload: Inputimg/mobileugv/7.jpg
Prompt: "navigate forward then turn left"
Mode: 2-Wheel Mobile Robot
Result: 77-frame navigation video
```

### Humanoid Video
```bash
Upload: Inputimg/humnoid/g1de2.jpg
Prompt: "walk forward"
Mode: General Image Analyzer
Result: 77-frame locomotion video
```

---

## Troubleshooting

**Port 5000 in use?**
```bash
lsof -ti:5000 | xargs kill -9
./START_HERE.sh  # This does it automatically
```

**Flask not found?**
```bash
../.venv/bin/uv pip install -r requirements.txt
```

**GPU out of memory?**
- Reduce frames from 144 to 77
- Lower resolution to 432×768
- Close other GPU applications

---

## File Outputs

All generated files saved to `outputs/`:

```
outputs/
├── <mode>_<timestamp>.mp4          # Generated video
├── <mode>_<timestamp>_prompt.txt   # Enhanced prompt
├── <mode>_<timestamp>_prompt.json  # Cosmos config
└── console.log                     # Generation logs
```

---

## Network Access

Find your IP:
```bash
ip addr show | grep inet
```

Access from other devices:
```
http://YOUR_IP:5000
```

**Note**: Authentication currently disabled. To enable, edit [app.py:19](app.py#L19):
```python
AUTH_ENABLED = True
AUTH_PASSWORD = 'your_secure_password'
```

---

## Architecture

```
User Input (Image + Prompt)
    ↓
Qwen2.5-VL-7B Analysis (~10 seconds)
    ↓
Enhanced Physics-Based Prompt (200-300 words)
    ↓
Cosmos Predict 2.5 Generation (~2 minutes)
    ↓
MP4 Video Output
```

**Key Components:**
- **Frontend**: HTML5 + JavaScript + CSS
- **Backend**: Flask 3.0 with HTTP streaming
- **AI Models**:
  - Qwen2.5-VL-7B (16GB VRAM) - Image analysis
  - Cosmos Predict 2.5 (14GB VRAM) - Video generation
- **Prompt Extenders**: 4 specialized Python scripts

---

## Code Structure

```
webinterfacemodule/
├── app.py                      # Flask server (line 314: --disable-guardrails fix)
├── START_HERE.sh               # Startup script
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Web UI
├── static/
│   ├── css/styles.css         # Styling
│   └── js/main.js             # Client logic
├── uploads/                   # Temporary image storage
└── outputs/                   # Generated videos
```

**Important Files:**
- [app.py:45](app.py#L45) - Qwen model path configuration
- [app.py:47-76](app.py#L47-L76) - Robot mode definitions
- [app.py:314](app.py#L314) - **Critical `--disable-guardrails` flag**

---

## Performance

**Generation Times:**
- Qwen VL Loading: ~6 seconds
- Image Analysis: ~10 seconds
- Cosmos Loading: ~20 seconds
- Video Generation: ~2 minutes
- **Total: ~2.5 minutes**

**Output Sizes:**
- SO-1 videos: ~400KB (77 frames)
- Mobile videos: ~1MB (77 frames)
- Humanoid videos: ~300KB (77 frames)

---

## Support

For detailed information:
- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **Updates**: [UPDATES.md](UPDATES.md)
- **Complete Guide**: [../ALLMODES.md](../ALLMODES.md)
- **Pipeline Tests**: [../Qwenvl+cosmos2.5/VIDEO_GENERATION_SUCCESS.md](../Qwenvl+cosmos2.5/VIDEO_GENERATION_SUCCESS.md)

---

## Credits

- **Cosmos Predict 2.5** - NVIDIA Physical AI
- **Qwen2.5-VL** - Alibaba Cloud Qwen Team
- **Web Interface** - Built for cosmos-predict2.5 robotics workflows

---

**Status: ✅ PRODUCTION READY**

All pipelines validated and tested. Ready for robotics video generation!
