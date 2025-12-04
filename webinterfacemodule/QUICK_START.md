# 🚀 Quick Start - Cosmos Predict 2.5 Web Interface

## ✅ Status: READY TO USE

The web interface is **fully operational** with validated pipelines.

---

## Start the Server

```bash
cd /home/humanoid/Downloads/cosmos-predict2.5/webinterfacemodule
./START_HERE.sh
```

Then open in your browser:
- **Local:** http://localhost:5000
- **Network:** http://YOUR_IP:5000 (find IP with `ip addr show`)

---

## How to Generate Videos

### Step 1: Select Robot Type
Choose from 4 validated modes:
- 🦾 **SO-1 Arm** - Single-arm manipulation
- 🤖 **2-Wheel Mobile** - Navigation and movement
- 🤝 **Bimanual UR3** - Dual-arm coordination
- 🔬 **General Analyzer** - Any robot or scene

### Step 2: Upload Image
- Drag & drop image into upload area
- Or click to browse files
- Supported: JPG, PNG, JPEG

### Step 3: Enter Prompt
Describe what the robot should do:
- SO-1: "pick the bottle and place it on the shelf"
- Mobile: "navigate forward 2 meters then turn left"
- General: "walk forward and avoid obstacles"

### Step 4: Adjust Settings (Optional)
- **Frames:** 77 (default, ~3 seconds) or 144 (~6 seconds)
- **Resolution:** 432×768 (default) or other presets
- **Seed:** Leave empty for random, or set number for reproducibility
- **Guidance:** 7.0 (default, balanced)

### Step 5: Generate
Click **"Generate Video"** and wait ~2-3 minutes.

### Step 6: Download
- Watch video preview in browser
- Download MP4 video file
- Download enhanced prompt text file

---

## What's New? (Dec 3, 2025)

✅ **Fixed:** Added `--disable-guardrails` flag - robotics prompts no longer blocked!
✅ **Updated:** Using Qwen2.5-VL-7B (16GB model) instead of older version
✅ **Validated:** All 4 robot modes tested with successful video generation
✅ **Improved:** Better startup script with automatic port cleanup

---

## Example Workflows

### Generate SO-1 Arm Video:
1. Upload: `Inputimg/so1/1.jpg`
2. Select: "SO-1 Arm (LeRobot)"
3. Prompt: "pick and place the bottle"
4. Generate → Wait 2-3 minutes → Download!

### Generate Mobile Robot Video:
1. Upload: `Inputimg/mobileugv/7.jpg`
2. Select: "2-Wheel Mobile Robot"
3. Prompt: "navigate forward then turn left"
4. Generate → Wait 2-3 minutes → Download!

### Generate Humanoid Video:
1. Upload: `Inputimg/humnoid/g1de2.jpg`
2. Select: "General Image Analyzer"
3. Prompt: "walk forward"
4. Generate → Wait 2-3 minutes → Download!

---

## Troubleshooting

### Port Already in Use?
```bash
# Kill existing server
lsof -ti:5000 | xargs kill -9

# Or use the startup script (it does this automatically)
./START_HERE.sh
```

### Flask Not Found?
```bash
# Install dependencies
../.venv/bin/uv pip install -r requirements.txt
```

### GPU Out of Memory?
- Reduce frames from 144 to 77
- Lower resolution from 1080p to 720p
- Close other GPU applications

---

## Performance

**Generation Time:** ~2-3 minutes total
- Qwen VL Analysis: ~10 seconds
- Cosmos Loading: ~20 seconds
- Video Generation: ~2 minutes

**Output Size:**
- SO-1 videos: ~400KB
- Mobile videos: ~1MB
- Humanoid videos: ~300KB

---

## Files & Locations

**Uploaded Images:** `webinterfacemodule/uploads/`
**Generated Videos:** `webinterfacemodule/outputs/`
**Logs:** `webinterfacemodule/outputs/console.log`

Each generation creates:
- `.mp4` - The generated video
- `_prompt.txt` - Enhanced physics-based prompt
- `_prompt.json` - Cosmos configuration used
- `config.yaml` - Detailed settings
- `console.log` - Generation logs

---

## Network Access

To access from other devices on your WiFi:

1. Find your IP:
   ```bash
   ip addr show | grep inet
   ```

2. Other devices can access at:
   ```
   http://YOUR_IP:5000
   ```

3. **Note:** Authentication is currently disabled. To enable it, edit `app.py`:
   ```python
   AUTH_ENABLED = True
   AUTH_USERNAME = 'admin'
   AUTH_PASSWORD = 'your_password_here'
   ```

---

## Support

For detailed information:
- **Updates:** [UPDATES.md](UPDATES.md)
- **Full README:** [README.md](README.md)
- **Pipeline Results:** [../Qwenvl+cosmos2.5/VIDEO_GENERATION_SUCCESS.md](../Qwenvl+cosmos2.5/VIDEO_GENERATION_SUCCESS.md)

---

**Ready to generate physics-based robotics videos? Run `./START_HERE.sh` now!** 🚀
