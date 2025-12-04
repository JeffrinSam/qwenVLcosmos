# 🚀 Quick Start Guide - Reasoning Cosmos

Get started in 3 simple steps!

## Step 1: Install Prerequisites

```bash
cd /home/humanoid/Downloads/cosmos-predict2.5/Qwen_instructor
python download_qwen_instructor.py
```

## Step 2: Run Interactive Pipeline

```bash
cd /home/humanoid/Downloads/cosmos-predict2.5
python reasoningcosmos/interactive_cosmos_pipeline.py
```

## Step 3: Follow the Prompts

```
Select Robot Type:
  [1] 🦾 3 DOF Manipulator
  [2] 🤖 Mobile Robot (UGV)  ← Choose this for your UGV
  [3] 🦿 Bimanual UR3

Enter choice [1-3]: 2

Enter image path: Inputimg/4.jpg

Your prompt: navigate forward and turn left
```

That's it! The system will:
1. ✅ Analyze your image with Qwen VL
2. ✅ Generate detailed physics-based prompt
3. ✅ Create Cosmos-compatible JSON
4. ✅ Optionally generate video immediately

## Example: Recreate Your UGV Video

Based on your existing config, here's how to use the new interface:

```bash
python reasoningcosmos/interactive_cosmos_pipeline.py
```

**When prompted:**
- Robot Type: `2` (Mobile Robot)
- Image: `Inputimg/4.jpg`
- Prompt: `pivot 180 degrees and drive toward camera`
- Advanced Settings: `y`
  - Frames: `77`
  - Seed: `42`
  - Guidance: `7`
  - Resolution: `432,768`
  - Autoregressive: `Y`

The system will automatically generate the same detailed prompt structure you had manually:
- ✅ Physical setup with UGV description
- ✅ Static camera at floor level
- ✅ Action vector with pivot and approach
- ✅ Ground plane constraint
- ✅ Proper negative prompts

## What's Different?

### Before (Manual)
You had to write this complex prompt manually:
```json
{
  "prompt": "PHYSICAL SIMULATION: GROUND ROBOT APPROACH. \n\n[SETUP]: The input image contains a grey wheeled UGV (Unmanned Ground Vehicle) on an office carpet. \n[CAMERA STATE]: The camera is a STATIC TRIPOD fixed at floor level. CAMERA VELOCITY = 0. The background walls and furniture are FROZEN and do not move.\n[ACTION VECTOR]: The UGV robot pivots 180 degrees to face the lens. It then accelerates along the Z-AXIS directly towards the static camera position. \n[OUTCOME]: The robot stays on the ground (planar movement) and gets significantly larger in the frame as it closes the distance to the viewer.",
  ...
}
```

### Now (Automatic)
Just type: **"pivot 180 degrees and drive toward camera"**

The Qwen VL model analyzes the image and generates all the physics details automatically!

## Batch Processing Example

Process multiple UGV images:

```bash
python reasoningcosmos/batch_cosmos_pipeline.py \
  --mode 2 \
  --input-dir Inputimg/ \
  --prompt "navigate forward" \
  --frames 77 \
  --guidance 7
```

Or use CSV for different prompts per image:

```bash
python reasoningcosmos/batch_cosmos_pipeline.py \
  --mode 2 \
  --csv-file reasoningcosmos/example_batch_tasks.csv \
  --run-inference
```

## Next Steps

- 📖 Read full documentation: [reasoningcosmos/README.md](README.md)
- 🎓 Learn about prompt extenders: [Qwen_instructor_7B/ROBOTICS_PROMPT_EXTENDERS_README.md](../Qwen_instructor_7B/ROBOTICS_PROMPT_EXTENDERS_README.md)
- 🔧 Customize for your robots: Edit prompt extender scripts

## Tips

1. **Be specific**: "slowly approach" vs "approach"
2. **Mention objects**: "avoid the box on left"
3. **Include direction**: "turn right 90 degrees"
4. **Describe speed**: "accelerate rapidly"

Enjoy simple, intelligent robot video generation! 🎉
