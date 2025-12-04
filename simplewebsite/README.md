# Cosmos Predict 2.5 - Simple Web Interface

A streamlined Flask-based web interface for generating videos from images using Cosmos Predict 2.5.

## Features

- **Drag & Drop Upload**: Easy image upload with drag-and-drop or file browser
- **All Advanced Settings Visible**: Full control over generation parameters
- **Password Protected**: Secure access for local network sharing
- **Real-time Progress**: Live status updates during video generation
- **Video Preview & Download**: View and download generated videos and configs
- **Organized File Storage**: All uploads and outputs saved in organized folders

## Quick Start

### 1. Start the Server

```bash
cd /home/humanoid/Downloads/cosmos-predict2.5/simplewebsite
./start_server.sh
```

The script will:
- Create a virtual environment if needed
- Install dependencies
- Display access URLs
- Start the Flask server

### 2. Access the Interface

**Local Access:**
```
http://127.0.0.1:5000
```

**Network Access (from other devices on same WiFi):**
```
http://<your-local-ip>:5000
```

Your local IP will be displayed when the server starts.

### 3. Login

When prompted, enter:
- **Username:** `admin`
- **Password:** `cosmos2025`

## How to Use

1. **Upload Image**
   - Drag and drop an image onto the upload area
   - Or click to browse and select a file
   - Supported formats: JPG, PNG, WEBP (max 50MB)

2. **Enter Prompt**
   - Describe the physical simulation you want to generate
   - Use detailed descriptions for best results

3. **Configure Advanced Settings**
   - **Negative Prompt**: Describe what you DON'T want
   - **Output Frames**: Number of frames to generate (77 ≈ 3.2 seconds)
   - **Autoregressive Mode**: ✓ Enable for longer videos (checked by default)
   - **Chunk Size/Overlap**: Control how video chunks are generated (shown when autoregressive is enabled)
   - **Resolution Preset**: Choose from predefined resolutions optimized for the 2B model
     - **720p Quality** (Default): Best quality, recommended for 2B model
     - **480p Quality**: Faster generation, good quality
     - **1080p Quality**: Highest quality (requires more GPU memory)
     - **Custom**: Set your own resolution
   - **Seed**: For reproducible results
   - **Guidance**: 0-7 scale (higher = closer to prompt)

4. **Generate**
   - Click "Generate Video"
   - You'll be redirected to a status page
   - Watch real-time progress
   - Video will preview automatically when complete

5. **Download**
   - Download the generated video
   - Download the JSON config for reproducibility
   - Generate another video or adjust settings

## File Organization

All files are saved in organized folders:

```
simplewebsite/
├── uploads/          # Uploaded images
│   └── {job_id}_{filename}.jpg
├── outputs/          # Generated content
│   └── img2world_{timestamp}/
│       ├── config.json
│       └── img2world_{timestamp}.mp4
└── logs/            # Application logs
```

## Resolution Presets

The interface includes optimized resolution presets based on Cosmos 2.5 2B model specifications:

### 720p Quality (Default - Recommended)
- **704 x 1280** (9:16 Vertical) - Default preset
- **1280 x 704** (16:9 Widescreen)
- **960 x 960** (1:1 Square)
- **960 x 704** (4:3 Landscape)
- **704 x 960** (3:4 Portrait)

### 480p Quality (Faster Generation)
- **432 x 768** (9:16 Vertical) - Good for testing
- **768 x 432** (16:9 Widescreen)
- **640 x 480** (4:3 Landscape)
- **480 x 640** (3:4 Portrait)
- **480 x 480** (1:1 Square)

### 1080p Quality (High Memory Required)
- **1056 x 1920** (9:16 Vertical)
- **1920 x 1056** (16:9 Widescreen)
- **1024 x 1024** (1:1 Square)

See dropdown menu for complete list including 512p, 720p Standard, and 480p Standard presets.

## Example Configuration

Based on your example, here are good default settings:

```
Prompt: "PHYSICAL SIMULATION: GROUND ROBOT APPROACH.

[SETUP]: The input image contains a grey wheeled UGV on an office carpet.
[CAMERA STATE]: Camera is STATIC TRIPOD at floor level. CAMERA VELOCITY = 0.
[ACTION VECTOR]: UGV pivots 180 degrees to face lens, then accelerates toward camera.
[OUTCOME]: Robot stays on ground and gets larger in frame."

Negative Prompt: "drone, aerial flight, hovering, camera dolly, camera moving forward, zooming camera, floating robot, flying robot, distorted wheels, morphing shape, shaky camera, motion blur on background, changing background geometry."

Settings:
- Frames: 77
- Enable Autoregressive: ✓ (checked by default)
- Chunk Size: 77
- Chunk Overlap: 1
- Resolution: 704 x 1280 (9:16 Vertical - Default) or 432 x 768 (9:16 - Faster)
- Seed: 42
- Guidance: 7
```

## Network Access

To allow others on your WiFi to access:

1. Start the server with `./start_server.sh`
2. Note your local IP address (displayed on startup)
3. Share the network URL: `http://<your-local-ip>:5000`
4. They'll be prompted for the username and password

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

## Troubleshooting

**Port Already in Use:**
If port 5000 is already in use, edit [app.py](app.py) and change the port:
```python
app.run(host='0.0.0.0', port=5001, ...)
```

**Permission Denied:**
Make sure the start script is executable:
```bash
chmod +x start_server.sh
```

**Can't Access from Network:**
- Verify your firewall allows connections on port 5000
- Make sure both devices are on the same WiFi network
- Try disabling VPN if active

**Generation Fails:**
- Check that Cosmos Predict 2.5 is properly installed
- Verify the inference script exists at `../examples/inference.py`
- Check console output in the status page for error details

## Directory Structure

```
simplewebsite/
├── app.py                 # Flask backend
├── start_server.sh        # Launch script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   ├── index.html        # Main interface
│   └── status.html       # Status page
├── static/
│   ├── css/
│   │   └── styles.css    # Styling
│   └── js/
│       └── main.js       # Frontend logic
├── uploads/              # Uploaded images
├── outputs/              # Generated videos
├── logs/                 # Application logs
└── venv/                 # Virtual environment (auto-created)
```

## Advanced Configuration

### Change Authentication

Edit [app.py](app.py) and modify:
```python
AUTH_USERNAME = 'admin'
AUTH_PASSWORD = 'your-new-password'
```

### Disable Authentication

Edit [app.py](app.py) and change the verify_password function:
```python
@auth.verify_password
def verify_password(username, password):
    return True  # Disable authentication
```

### Change Upload Size Limit

Edit [app.py](app.py):
```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

## Credits

- **Cosmos Predict 2.5** by NVIDIA
- **Web Interface** created for simple image-to-world generation

## License

This web interface is provided as-is for use with Cosmos Predict 2.5.
