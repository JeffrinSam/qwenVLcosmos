# Qwen VL + Cosmos 2.5 Complete Pipelines

End-to-end pipelines that combine **Qwen2.5-VL-7B vision analysis** with **Cosmos Predict 2.5 video generation** to create physics-based robot videos from a single image.

## Overview

These pipelines provide a complete solution:

```
Input Image → Qwen VL Analysis → Enhanced Prompt → Cosmos Generation → Output Video
```

**What makes this special:**
- 🔍 **Vision-based prompt enhancement** - Qwen VL analyzes the image and generates detailed, physics-based prompts
- 🤖 **Embodiment-specific optimization** - Specialized pipelines for different robot types
- 🎬 **Automatic video generation** - One command from image to video
- ⚙️ **Configurable parameters** - Full control over resolution, frames, guidance, etc.

## Three Pipelines

### 1. SO-1 Arm Pipeline
**Location:** `so1_arm/complete_pipeline.py`

Optimized for single-arm manipulation robots (like LeRobot SO-1):
- Pick-and-place operations
- Precision assembly
- Tabletop manipulation
- Gripper control

**Example:**
```bash
cd so1_arm
python complete_pipeline.py --image path/to/so1_arm.jpg --prompt "pick red cube"
```

### 2. Mobile Robot Pipeline
**Location:** `mobile_robot/complete_pipeline.py`

Optimized for 2-wheel differential drive robots (UGVs):
- Navigation and path following
- Turn-in-place maneuvers
- Approach/avoidance behaviors
- Warehouse/delivery robots

**Example:**
```bash
cd mobile_robot
python complete_pipeline.py --image path/to/ugv.jpg --prompt "navigate forward and turn"
```

### 3. General Pipeline
**Location:** `general/complete_pipeline.py`

Works with ANY robot or scene:
- Bimanual robots
- Quadrupeds
- Humanoids
- Industrial arms
- Custom embodiments
- General scenes

**Example:**
```bash
cd general
python complete_pipeline.py --image path/to/robot.jpg --prompt "desired action"
```

## Quick Start

### Prerequisites

1. **Qwen2.5-VL-7B model** installed in `Qwen_instructor_7B/`
2. **Cosmos Predict 2.5** installed and working
3. **CUDA-capable GPU** (recommended)

### Basic Usage

1. **Choose your pipeline** based on robot type:
   - SO-1 arm → `so1_arm/`
   - 2-wheel mobile → `mobile_robot/`
   - Any other → `general/`

2. **Run the pipeline:**
   ```bash
   cd <pipeline_folder>
   python complete_pipeline.py --image path/to/image.jpg --prompt "what you want"
   ```

3. **Find your video** in `../outputs/<job_name>/`

## Detailed Usage

### SO-1 Arm Examples

```bash
# Basic pick-and-place (vision only, no user prompt needed)
python complete_pipeline.py --image so1_picking.jpg

# With specific guidance
python complete_pipeline.py --image so1_assembly.jpg --prompt "precise positioning for assembly"

# Longer video (121 frames ≈ 5 seconds)
python complete_pipeline.py --image so1_task.jpg --prompt "multi-step manipulation" --frames 121

# Custom resolution
python complete_pipeline.py --image so1_arm.jpg --prompt "pick object" --resolution 768,432
```

### Mobile Robot Examples

```bash
# Navigate forward
python complete_pipeline.py --image ugv_indoor.jpg --prompt "navigate forward"

# Pivot and approach
python complete_pipeline.py --image ugv_office.jpg --prompt "pivot 180 degrees and approach camera"

# Complex navigation
python complete_pipeline.py --image warehouse_robot.jpg --prompt "navigate to target and stop" --frames 144

# Fast generation (480p)
python complete_pipeline.py --image ugv.jpg --prompt "turn right" --resolution 432,768 --frames 77
```

### General Examples

```bash
# Bimanual robot
python complete_pipeline.py --image bimanual.jpg --prompt "both arms coordinate to assemble"

# Quadruped
python complete_pipeline.py --image quadruped.jpg --prompt "walk forward steadily"

# Humanoid
python complete_pipeline.py --image humanoid.jpg --prompt "reach and grasp with right hand"

# Any custom robot
python complete_pipeline.py --image custom_robot.jpg --prompt "perform task" --frames 121
```

## Command-Line Arguments

All pipelines support the same arguments:

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--image` | `-i` | Input image path | **Required** |
| `--prompt` | `-p` | User guidance/action description | (empty for SO-1/mobile)† |
| `--frames` | `-f` | Number of output frames | 77 |
| `--resolution` | `-r` | Resolution as "height,width" | 432,768 |
| `--seed` | | Random seed | 42 |
| `--guidance` | | Guidance scale (0-7) | 7 |
| `--no-autoregressive` | | Disable autoregressive mode | (enabled) |
| `--chunk-size` | | Chunk size for autoregressive | 77 |
| `--chunk-overlap` | | Chunk overlap frames | 1 |
| `--output-dir` | `-o` | Custom output directory | ../outputs/ |

† The general pipeline **requires** `--prompt`, while SO-1/mobile can work with vision only.

## Output Structure

Each job creates a timestamped folder in `outputs/`:

```
outputs/
└── so1_arm_20251203_120000/
    ├── enhanced_prompt.txt      # Qwen VL generated prompt
    ├── cosmos_config.json        # Cosmos Predict configuration
    └── so1_arm_20251203_120000.mp4  # Generated video
```

## Resolution Presets

Common resolutions for Cosmos 2.5 2B model:

| Resolution | Format | Use Case |
|------------|--------|----------|
| 704,1280 | 9:16 Vertical | Default (best quality) |
| 432,768 | 9:16 Vertical | Fast generation |
| 768,432 | 16:9 Widescreen | Landscape view |
| 1280,704 | 16:9 Widescreen | HD landscape |
| 960,960 | 1:1 Square | Centered view |

## Frame Count Guidelines

| Frames | Duration | Use Case |
|--------|----------|----------|
| 77 | ~3.2s | Quick actions, single movements |
| 121 | ~5s | Multi-step tasks |
| 144 | ~6s | Complex sequences |
| 200+ | 8s+ | Extended operations (requires more memory) |

## How It Works

### Step-by-Step Process

1. **Load Qwen VL Model**
   - Loads Qwen2.5-VL-7B from `Qwen_instructor_7B/`
   - Initializes vision processor

2. **Analyze Image**
   - Processes input image
   - Identifies robot type, pose, scene elements
   - Generates detailed scene understanding

3. **Generate Enhanced Prompt**
   - Combines vision analysis + user guidance
   - Creates physics-based Cosmos-style prompt
   - Includes camera state, motion vectors, physics constraints
   - Optimized for each embodiment type

4. **Create Cosmos Config**
   - Builds JSON configuration
   - Sets resolution, frames, seed, guidance
   - Includes embodiment-specific negative prompts

5. **Run Cosmos Predict**
   - Calls `examples/inference.py`
   - Generates video with autoregressive mode
   - Streams real-time progress

6. **Output Results**
   - Saves enhanced prompt (.txt)
   - Saves configuration (.json)
   - Saves generated video (.mp4)

### Prompt Enhancement Examples

**User Input:**
```
Image: so1_arm_picking.jpg
Prompt: "pick red cube"
```

**Qwen VL Enhanced Prompt:**
```
STATIC CAMERA: Fixed position at tabletop height, 45-degree angle viewing workspace.
CAMERA VELOCITY = 0. Background remains frozen throughout sequence.

[ACTION VECTOR]: SO-1 arm starts at rest position 30cm above red cube. End-effector
descends vertically at 5cm/s over 2.0 seconds, approaching cube center. Gripper opens
to 8cm width. At t=2.0s, gripper reaches cube surface, closes smoothly to 5.5cm over
0.5 seconds, applying 10N force for secure grasp. Arm lifts vertically at 8cm/s for
1.5 seconds, raising cube 12cm above table. Motion ends with cube suspended, gripper
maintaining grasp.

[PHYSICS CONSTRAINTS]: Gravity acts on cube (98g, rigid body). Smooth acceleration
from 0 to 5cm/s over 0.3s. No instant motion or teleportation. Gripper applies
adequate force for lift. Table surface remains static.
```

## Troubleshooting

### Common Issues

**1. Model not found**
```
Error: Failed to load model
```
**Solution:** Ensure Qwen2.5-VL-7B is in `../../Qwen_instructor_7B/`

**2. CUDA out of memory**
```
Error: CUDA out of memory
```
**Solutions:**
- Reduce resolution: `--resolution 432,768`
- Reduce frames: `--frames 77`
- Disable autoregressive: `--no-autoregressive`

**3. Cosmos inference fails**
```
Error: Cosmos Predict failed with return code 1
```
**Solution:** Check that Cosmos Predict 2.5 is properly installed and `examples/inference.py` works

**4. Invalid image**
```
Error: Image not found
```
**Solution:** Use absolute path or verify file exists

## Performance Tips

### For Faster Generation

1. **Use 480p resolution:** `--resolution 432,768`
2. **Reduce frames:** `--frames 77` (instead of 121+)
3. **Lower guidance:** `--guidance 5` (instead of 7)
4. **Disable autoregressive** for short clips: `--no-autoregressive`

### For Best Quality

1. **Use 720p resolution:** `--resolution 704,1280` (default)
2. **Max guidance:** `--guidance 7`
3. **More frames** for smooth motion: `--frames 121`
4. **Enable autoregressive:** (enabled by default)

## Comparison with Manual Mode

| Feature | Manual Mode | Qwen VL Pipeline |
|---------|-------------|------------------|
| **Input** | Image + full prompt | Image + brief guidance (or vision only) |
| **Prompt quality** | Depends on user skill | Consistently detailed |
| **Physics accuracy** | User must specify | Automatically inferred |
| **Embodiment knowledge** | User must know details | Model understands robot type |
| **Ease of use** | Requires expertise | Beginner-friendly |
| **Flexibility** | Full control | Automated with overrides |

## Advanced Usage

### Custom Negative Prompts

Edit the pipeline script to customize negative prompts:

```python
cosmos_config = {
    # ...
    "negative_prompt": "your custom negative prompt here",
}
```

### Batch Processing

Create a batch script:

```bash
#!/bin/bash
for img in images/*.jpg; do
    python complete_pipeline.py --image "$img" --prompt "action"
done
```

### Integration with Other Tools

The pipelines output standard Cosmos JSON configs, which can be:
- Modified and re-run
- Used with other Cosmos tools
- Integrated into larger workflows

## Directory Structure

```
Qwenvl+cosmos2.5/
├── README.md                 # This file
├── so1_arm/
│   └── complete_pipeline.py  # SO-1 arm pipeline
├── mobile_robot/
│   └── complete_pipeline.py  # Mobile robot pipeline
├── general/
│   └── complete_pipeline.py  # General embodiment pipeline
├── outputs/                  # Generated videos (created automatically)
│   ├── so1_arm_TIMESTAMP/
│   ├── mobile_robot_TIMESTAMP/
│   └── general_TIMESTAMP/
└── configs/                  # Optional custom configs
```

## Dependencies

- Python 3.10+
- PyTorch with CUDA support
- Transformers (for Qwen VL)
- PIL/Pillow
- Cosmos Predict 2.5
- Qwen2.5-VL-7B model

## Credits

- **Qwen2.5-VL** by Alibaba Cloud
- **Cosmos Predict 2.5** by NVIDIA
- **Integration** for robotics video generation

## License

Follows the licenses of constituent projects:
- Qwen2.5-VL: Apache 2.0
- Cosmos Predict 2.5: Apache 2.0

## Support

For issues specific to:
- **Qwen VL model:** Check Qwen documentation
- **Cosmos Predict:** Check Cosmos Predict documentation
- **This pipeline:** Check console output and error messages

## Contributing

To add a new embodiment-specific pipeline:

1. Copy `general/complete_pipeline.py`
2. Import appropriate prompt extender from `Qwen_instructor_7B/`
3. Customize system prompts and negative prompts
4. Test with representative images
5. Document usage examples

---

**Quick Links:**
- [Cosmos Predict Documentation](https://docs.nvidia.com/cosmos/)
- [Qwen VL Model](https://huggingface.co/Qwen)
- [Parent Project README](../README.md)
