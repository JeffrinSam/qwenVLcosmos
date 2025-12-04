# 🎬 Reasoning Cosmos - Interactive Video Generation Interface

**Simplified interface for generating robotic videos with Cosmos Predict 2.5**

This directory contains interactive tools that make it easy to generate physics-based robotic videos without writing complex prompts manually.

## 🚀 Quick Start

### Interactive Mode (Recommended)

Run the interactive pipeline for a guided experience:

```bash
cd /home/humanoid/Downloads/cosmos-predict2.5
python reasoningcosmos/interactive_cosmos_pipeline.py
```

**You'll be prompted for:**
1. **Robot Type**: Choose between 3 DOF, Mobile Robot, or Bimanual UR3
2. **Image**: Path to your robot image
3. **Simple Prompt**: Natural language like "pick up the apple using right hand"
4. **Settings**: Optional advanced configuration
5. **Generate**: Automatically create video with Cosmos

### Example Session

```
🎬 INTERACTIVE COSMOS PIPELINE - Robotics Video Generation
=======================================================================

Select Robot Type:

  [1] 🦾 3 DOF Manipulator
      → SCARA, delta, cartesian robots for pick-and-place

  [2] 🤖 Mobile Robot (UGV)
      → Wheeled/tracked robots for navigation

  [3] 🦿 Bimanual UR3
      → Dual-arm coordination and manipulation

Enter choice [1-3]: 2

Image Input:
Enter image path (or drag & drop): Inputimg/ugv/4.jpg
✓ Image found: /home/humanoid/Downloads/cosmos-predict2.5/Inputimg/ugv/4.jpg

Task Description:
Enter a simple, natural language description of what the robot should do.
Examples:
  • 'pick up the apple using right hand'
  • 'navigate forward and turn left to avoid obstacle'
  • 'both arms lift the box together'

Your prompt: navigate forward toward the camera
✓ Prompt received

Advanced Settings (Optional):
Configure advanced settings? [y/N]: n

Processing...
=======================================================================
Running Mobile Robot (UGV) Analysis...
🧠 Analyzing image with Qwen2.5-VL...
✓ Prompt generation complete!

Generate video now? [Y/n]: y

Running Cosmos Inference...
🎬 Generating video (this may take several minutes)...

✓ Video generation complete!
📁 Output directory: reasoningcosmos/outputs/cosmos_2_4_video
🎥 Generated videos:
   cosmos_2_4_video/output.mp4

🎉 SUCCESS! Video generated successfully!
```

## 📁 What You Get

### Interactive Pipeline Outputs

For each run, you get:

```
reasoningcosmos/outputs/
├── cosmos_2_4_prompt.txt          # Human-readable enhanced prompt
├── cosmos_2_4_prompt.json         # Cosmos-compatible configuration
└── cosmos_2_4_video/              # Generated video folder
    ├── output.mp4                 # Final video
    └── metadata.json              # Generation metadata
```

## 🔧 Tools Available

### 1. Interactive Pipeline (`interactive_cosmos_pipeline.py`)

**Best for**: Single images, learning the system, custom tasks

**Features**:
- ✅ Step-by-step guided interface
- ✅ Automatic robot type detection from your choice
- ✅ Simple natural language prompts
- ✅ Optional advanced settings
- ✅ Direct video generation
- ✅ Colorized terminal output

**Usage**:
```bash
python reasoningcosmos/interactive_cosmos_pipeline.py
```

### 2. Batch Pipeline (`batch_cosmos_pipeline.py`)

**Best for**: Processing multiple images, creating datasets

**Features**:
- ✅ Process entire directories
- ✅ CSV-based task lists
- ✅ Consistent settings across batch
- ✅ Optional automatic inference

**Usage - Directory Mode**:
```bash
# Process all images in a directory with same prompt
python reasoningcosmos/batch_cosmos_pipeline.py \
  --mode 2 \
  --input-dir Inputimg/ugv \
  --prompt "navigate forward and avoid obstacles"
```

**Usage - CSV Mode**:
```bash
# Create tasks.csv:
# image_path,prompt
# Inputimg/ugv/scene1.jpg,"navigate to the door"
# Inputimg/ugv/scene2.jpg,"turn left at intersection"

python reasoningcosmos/batch_cosmos_pipeline.py \
  --mode 2 \
  --csv-file tasks.csv \
  --run-inference
```

## 🤖 Robot Modes

### Mode 1: 3 DOF Manipulator
- SCARA robots
- Delta robots
- Cartesian systems
- Pick-and-place operations

**Example prompts**:
- "pick up the red block and place it in the bin"
- "move to home position"
- "grab the part with the gripper"

### Mode 2: Mobile Robot (UGV)
- Wheeled platforms
- Tracked vehicles
- Differential drive robots
- Warehouse/delivery bots

**Example prompts**:
- "navigate forward and turn left to avoid obstacle"
- "approach the table slowly"
- "rotate 180 degrees and move backward"

### Mode 3: Bimanual UR3
- Dual UR3 robot arms
- Coordinated manipulation
- Assembly tasks
- Object handoff

**Example prompts**:
- "both arms lift the box together"
- "left arm holds the part while right arm screws it"
- "transfer the object from left hand to right hand"

## ⚙️ Advanced Settings

When prompted "Configure advanced settings?", you can customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `num_output_frames` | 77 | Number of video frames to generate |
| `seed` | 42 | Random seed for reproducibility |
| `guidance` | 7 | Guidance scale (higher = more prompt adherence) |
| `resolution` | 432,768 | Video resolution (height,width) |
| `enable_autoregressive` | true | Enable longer video generation |

## 📊 Batch Processing Examples

### Example 1: Process Directory
```bash
python reasoningcosmos/batch_cosmos_pipeline.py \
  --mode 2 \
  --input-dir Inputimg/ugv \
  --prompt "autonomous navigation in warehouse" \
  --frames 121 \
  --guidance 8
```

### Example 2: CSV Task List
Create `my_tasks.csv`:
```csv
image_path,prompt
Inputimg/3dof/assembly1.jpg,pick up the gear and place on shaft
Inputimg/3dof/assembly2.jpg,insert the pin into the hole
Inputimg/3dof/assembly3.jpg,remove the finished part
```

Run:
```bash
python reasoningcosmos/batch_cosmos_pipeline.py \
  --mode 1 \
  --csv-file my_tasks.csv \
  --run-inference
```

## 🎯 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  1. USER INPUT                                              │
│  • Image: robot_scene.jpg                                   │
│  • Simple Prompt: "pick up the apple"                       │
│  • Robot Type: Mobile Robot                                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  2. QWEN2.5-VL VISION ANALYSIS                             │
│  • Analyzes image: robot type, environment, objects         │
│  • Understands task from natural language                   │
│  • Applies robot-specific physics knowledge                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  3. INTELLIGENT PROMPT GENERATION                          │
│  • [PHYSICAL SETUP]: Detailed scene description             │
│  • [CAMERA STATE]: Camera positioning                       │
│  • [ACTION VECTOR]: Physics-based motion planning           │
│  • [CONSTRAINTS]: Robot kinematics, collision avoidance     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  4. COSMOS PREDICT 2.5 VIDEO GENERATION                    │
│  • Flow-based physics simulation                            │
│  • Generates realistic robot motion video                   │
│  • Output: MP4 video file                                   │
└─────────────────────────────────────────────────────────────┘
```

## 💡 Tips for Best Results

### Image Quality
- ✅ Well-lit scenes showing full robot
- ✅ Clear view of workspace and objects
- ✅ Include context (floor, walls, obstacles)
- ❌ Avoid blurry or dark images

### Prompt Writing
- ✅ Use simple, clear action verbs
- ✅ Specify directions: "left", "right", "forward"
- ✅ Mention objects by name: "red apple", "wooden box"
- ✅ Include speed if important: "slowly approach"
- ❌ Avoid overly complex multi-step tasks

### Settings Tuning
- **More frames** (121-241): Longer videos, slower motion
- **Higher guidance** (8-10): Stricter prompt following
- **Lower guidance** (5-6): More natural variation
- **Different seeds**: Try various seeds for different results

## 🔍 Comparing with Manual Approach

### Traditional Approach (Complex)
```json
{
  "prompt": "PHYSICAL SIMULATION: GROUND ROBOT APPROACH. [SETUP]: The input image contains a grey wheeled UGV (Unmanned Ground Vehicle) on an office carpet. [CAMERA STATE]: The camera is a STATIC TRIPOD fixed at floor level. CAMERA VELOCITY = 0. The background walls and furniture are FROZEN and do not move. [ACTION VECTOR]: The UGV robot pivots 180 degrees to face the lens. It then accelerates along the Z-AXIS directly towards the static camera position. [OUTCOME]: The robot stays on the ground (planar movement) and gets significantly larger in the frame as it closes the distance to the viewer.",
  "negative_prompt": "drone, aerial flight, hovering, camera dolly..."
}
```

### Reasoning Cosmos (Simple)
```
Image: ugv_scene.jpg
Prompt: "turn around and drive toward camera"
→ Automatically generates detailed physics-based prompt!
```

## 🐛 Troubleshooting

### Issue: "Model not found"
**Solution**: Download Qwen model first:
```bash
cd Qwen_instructor
python download_qwen_instructor.py
```

### Issue: "CUDA out of memory"
**Solution**: Use CPU mode or reduce resolution:
```bash
# Edit the prompt extender to use CPU
--device cpu
```

### Issue: "Video not generated"
**Solution**: Check Cosmos installation:
```bash
# Verify Cosmos models are downloaded
ls -lh ~/.cache/cosmos/
```

### Issue: "Prompt not detailed enough"
**Solution**: Add more context to your simple prompt:
```
Instead of: "move forward"
Try: "slowly move forward 2 meters while avoiding the box on the left"
```

## 🔧 Customization

### Add Custom Robot Type

1. Create new prompt extender in `Qwen_instructor_7B/`:
```python
# prompt_extender_custom_robot.py
# Copy and modify existing extender
```

2. Add to `interactive_cosmos_pipeline.py`:
```python
self.robot_modes = {
    '4': {
        'name': 'My Custom Robot',
        'script': 'prompt_extender_custom_robot.py',
        'description': 'Description here',
        'icon': '🤖'
    }
}
```

### Modify Default Settings

Edit `interactive_cosmos_pipeline.py` line ~240:
```python
settings = {
    'num_output_frames': 121,  # Change default frames
    'seed': 42,
    'guidance': 8.5,  # Increase guidance
    'resolution': '432,768',
    'enable_autoregressive': True,
}
```

## 📚 Related Documentation

- [Parent README - Robotics Prompt Extenders](../Qwen_instructor_7B/ROBOTICS_PROMPT_EXTENDERS_README.md)
- [Cosmos Inference Guide](../docs/inference.md)
- [Cosmos Post-Training Guide](../docs/post-training.md)

## 🎓 Learning Resources

### Start Here
1. Run interactive pipeline with example images
2. Try all three robot modes
3. Experiment with different prompts
4. Adjust advanced settings to see effects

### Next Steps
1. Use batch processing for datasets
2. Integrate generated videos into training pipeline
3. Fine-tune Cosmos on your specific robot (see post-training docs)

## 📝 Example Workflows

### Workflow 1: Quick Prototype
```bash
# 1. Run interactive mode
python reasoningcosmos/interactive_cosmos_pipeline.py

# 2. Select robot, provide image and prompt
# 3. Generate video instantly
# 4. Review and iterate
```

### Workflow 2: Dataset Creation
```bash
# 1. Prepare CSV with 100 tasks
# 2. Run batch processor
python reasoningcosmos/batch_cosmos_pipeline.py \
  --mode 2 --csv-file dataset.csv --run-inference

# 3. Outputs ready for training
```

### Workflow 3: Comparison Testing
```bash
# Test different robot types on same image
for mode in 1 2 3; do
  python reasoningcosmos/interactive_cosmos_pipeline.py \
    --mode $mode --image test.jpg --prompt "move forward"
done
```

## 🚦 Status

- ✅ Interactive pipeline - **Ready**
- ✅ Batch processing - **Ready**
- ✅ CSV task lists - **Ready**
- ✅ Auto inference - **Ready**
- 🚧 GUI interface - **Future**
- 🚧 Real-time preview - **Future**

## 📧 Support

If you encounter issues:
1. Check this README's troubleshooting section
2. Review [main Cosmos documentation](../docs/)
3. Ensure all prerequisites are installed
4. Check Qwen model is downloaded

---

**Created for Cosmos Predict 2.5**
*Making physics-based robot video generation accessible to everyone*
