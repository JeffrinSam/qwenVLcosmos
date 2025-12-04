# Robotics-Specialized Prompt Extenders for Cosmos Predict 2.5

This directory contains three specialized prompt extenders designed for different robotics applications. Each prompt extender is available in **TWO MODES**:

1. **Image + Prompt Mode**: Analyzes images using Qwen2.5-VL vision capabilities and generates physics-aware prompts
2. **Text-Only Mode**: Extends simple text prompts into detailed Cosmos prompts without requiring an image

Both modes generate prompts optimized for Cosmos Predict 2.5 video generation, following official NVIDIA guidelines.

## Understanding Cosmos Predict 2.5

**Cosmos Predict 2.5** is NVIDIA's flow-based world foundation model that generates physically realistic videos from text, images, or video inputs. It's specifically designed for Physical AI applications including:
- Autonomous vehicles
- Robotic manipulation
- World simulation and prediction

### Key Requirements for Cosmos Prompts:

1. **Physical Setup**: Detailed scene description with objects, spatial relationships, materials
2. **Camera State**: Camera position, movement, velocity (often static for robotics)
3. **Action Vector**: Realistic motion trajectories and physics-based actions
4. **Physics Constraints**: Gravity, momentum, material properties, motion laws
5. **Visual Quality**: Lighting, motion blur, depth of field, resolution

## Two Modes of Operation

### Mode 1: Image + Prompt (Vision Analysis)

**Scripts**: `prompt_extender_*_<robot_type>.py`

**Best for**:
- You have an existing robot image showing the scene
- Want Qwen2.5-VL to analyze the visual context
- Need scene-specific details inferred from the image
- Converting dataset images to video prompts

**How it works**:
1. Analyzes image with Qwen2.5-VL vision encoder
2. Identifies robot configuration, objects, workspace
3. Infers spatial relationships and likely tasks
4. Generates detailed prompt based on visual analysis
5. Uses `image2world` inference type for Cosmos

**Usage Example**:
```bash
python prompt_extender_mobile_robot.py --image Inputimg/ugv/warehouse.jpg --prompt "navigate forward"
```

### Mode 2: Text-Only (Prompt Extension)

**Scripts**: `prompt_extender_*_<robot_type>_text.py`

**Best for**:
- You have a clear text description but no image
- Want to extend simple prompts into detailed Cosmos format
- Prototyping robot behaviors without images
- Quick prompt generation for text2world inference

**How it works**:
1. Takes simple text input (e.g., "pick up red cube")
2. Uses Qwen2.5-VL language understanding to expand
3. Infers logical camera positions and scene setup
4. Generates structured prompt following Cosmos guidelines
5. Uses `text2world` inference type for Cosmos

**Usage Example**:
```bash
python prompt_extender_mobile_robot_text.py --prompt "navigate forward and turn left"
```

### Choosing the Right Mode

| Scenario | Recommended Mode | Reasoning |
|----------|------------------|-----------|
| Have robot images from dataset | Image + Prompt | Leverages visual context |
| Describing hypothetical behavior | Text-Only | No image needed |
| Converting existing robot footage | Image + Prompt | Analyzes actual scene |
| Rapid prototyping tasks | Text-Only | Faster iteration |
| Need exact scene details | Image + Prompt | Vision analysis provides specifics |
| Clear textual requirements | Text-Only | Direct prompt control |

## Three Specialized Prompt Extenders

### 1. 3 DOF Manipulator

**Purpose**: Optimized for simple 3 degree-of-freedom robotic manipulators used in pick-and-place and assembly tasks.

**Target Robots**:
- SCARA robots
- Delta robots
- Cartesian coordinate systems
- Simple planar manipulators

**Key Focus Areas**:
- Limited workspace (planar or semi-spatial motion)
- Simple end-effectors (grippers, suction cups)
- Point-to-point motion patterns
- Precision positioning

**Usage - Image + Prompt Mode**:
```bash
# Analyze image and generate prompt
python prompt_extender_3dof_manipulator.py --image Inputimg/3dof/pick_place.jpg
python prompt_extender_3dof_manipulator.py --image Inputimg/3dof/assembly.jpg --prompt "focus on precision positioning" --verbose
```

**Usage - Text-Only Mode**:
```bash
# Extend text prompt without image
python prompt_extender_3dof_manipulator_text.py --prompt "pick up red cube and place in box"
python prompt_extender_3dof_manipulator_text.py --prompt "precise assembly of small parts" --verbose
```

**Output Files**:
- `3dof_*_prompt.txt`: Enhanced text prompt
- `3dof_*_prompt.json`: Cosmos-compatible JSON configuration

---

### 2. Mobile Robot (UGV)

**Purpose**: Optimized for wheeled and tracked mobile robots (UGVs) performing autonomous navigation.

**Target Robots**:
- Differential drive robots
- 4-wheel drive platforms
- Tracked vehicles
- Mecanum wheel robots
- Warehouse/delivery robots

**Key Focus Areas**:
- Planar ground motion with gravity constraint
- Wheel/track contact physics and traction
- Turning dynamics and velocity profiles
- Obstacle avoidance and navigation
- Camera perspectives (onboard vs. external)

**Usage - Image + Prompt Mode**:
```bash
# Analyze robot image and generate navigation prompt
python prompt_extender_mobile_robot.py --image Inputimg/ugv/warehouse_bot.jpg
python prompt_extender_mobile_robot.py --image Inputimg/ugv/navigation.jpg --prompt "autonomous obstacle avoidance" --verbose
```

**Usage - Text-Only Mode**:
```bash
# Extend navigation prompt without image
python prompt_extender_mobile_robot_text.py --prompt "navigate forward 2 meters then turn left"
python prompt_extender_mobile_robot_text.py --prompt "patrol warehouse aisle avoiding obstacles" --verbose
```

**Output Files**:
- `mobile_robot_*_prompt.txt`: Enhanced text prompt
- `mobile_robot_*_prompt.json`: Cosmos-compatible JSON configuration

---

### 3. Bimanual UR3

**Purpose**: Optimized for dual-arm Universal Robots UR3 systems performing coordinated manipulation.

**Target Robots**:
- Dual UR3 collaborative robot arms
- 6 DOF per arm (12 DOF total system)
- Coordinated manipulation tasks

**Key Focus Areas**:
- Dual-arm coordination (synchronized, sequential, independent, handoff)
- Collision avoidance between arms
- Complex manipulation tasks (assembly, object transfer)
- Workspace overlap and shared zones
- UR3-specific constraints (500mm reach, 3kg payload)

**Usage - Image + Prompt Mode**:
```bash
# Analyze dual-arm setup image and generate coordination prompt
python prompt_extender_bimanual_ur3.py --image Inputimg/bimanual/assembly_task.jpg
python prompt_extender_bimanual_ur3.py --image Inputimg/bimanual/handoff.jpg --prompt "coordinated object transfer" --verbose
```

**Usage - Text-Only Mode**:
```bash
# Extend dual-arm task prompt without image
python prompt_extender_bimanual_ur3_text.py --prompt "both arms grasp object simultaneously"
python prompt_extender_bimanual_ur3_text.py --prompt "left arm holds part while right arm assembles" --verbose
```

**Output Files**:
- `bimanual_ur3_*_prompt.txt`: Enhanced text prompt
- `bimanual_ur3_*_prompt.json`: Cosmos-compatible JSON configuration

---

## Installation & Prerequisites

### 1. Install Qwen Model
First, download the Qwen2.5-VL model:
```bash
cd /home/humanoid/Downloads/cosmos-predict2.5/Qwen_instructor
python download_qwen_instructor.py
```

### 2. Install Dependencies
```bash
pip install torch transformers accelerate pillow
```

### 3. Prepare Your Images
Organize your robotics images in appropriate folders:
```
Inputimg/
├── 3dof/          # 3 DOF manipulator images
├── ugv/           # Mobile robot images
└── bimanual/      # Bimanual UR3 images
```

## How It Works

### Step 1: Vision Analysis
Each specialized prompt extender uses **Qwen2.5-VL** (a vision-language model) to:
- Analyze the input image
- Identify robot type and configuration
- Understand the scene and environment
- Detect objects and spatial relationships
- Infer likely manipulation or navigation tasks

### Step 2: Robotics-Specific Processing
Based on the robot type, the extender applies specialized knowledge:
- **3 DOF**: Focus on planar motion constraints, simple trajectories
- **Mobile Robot**: Emphasize ground contact, traction, navigation physics
- **Bimanual UR3**: Consider dual-arm coordination, collision avoidance, handoff protocols

### Step 3: Cosmos Prompt Generation
The extender generates a structured prompt with:
- **[PHYSICAL SETUP]**: Complete scene description
- **[CAMERA STATE]**: Camera configuration
- **[ACTION VECTOR]**: Detailed motion planning
- **[PHYSICS CONSTRAINTS]**: Material properties, dynamics
- **[ROBOT-SPECIFIC SECTIONS]**: Additional constraints for each robot type

### Step 4: Output Generation
Two files are created:
1. **TXT file**: Human-readable enhanced prompt
2. **JSON file**: Cosmos-compatible configuration for immediate inference

## Interactive Pipeline (Recommended)

The easiest way to use the prompt extenders is through the **interactive pipeline** which guides you through mode selection:

```bash
cd reasoningcosmos
python interactive_cosmos_pipeline.py
```

**Interactive Workflow**:
1. **Select Mode**: Choose between Image+Prompt or Text-Only
2. **Select Robot Type**: Choose 3 DOF, Mobile Robot, or Bimanual UR3
3. **Provide Input**: Image path (if Image+Prompt mode) or skip (if Text-Only)
4. **Enter Prompt**: Describe the task
5. **Configure Settings**: Video length, resolution, etc.
6. **Generate**: Automatically creates prompt and runs Cosmos inference

The interactive pipeline seamlessly handles mode selection and calls the appropriate script version.

## Using with Cosmos Predict 2.5 (Manual)

Once you've generated the JSON files manually, use them with Cosmos Predict:

```bash
# Image2World: Run inference with image + generated prompt
python examples/inference.py \
  -i Qwen_instructor/mobile_robot_warehouse_bot_prompt.json \
  -o outputs/mobile_robot_navigation

# Text2World: Run inference with text-only generated prompt
python examples/inference.py \
  -i Qwen_instructor/mobile_robot_navigation_prompt.json \
  -o outputs/mobile_robot_text

# Multi-GPU inference
torchrun --nproc_per_node=8 examples/inference.py \
  -i Qwen_instructor/bimanual_ur3_assembly_prompt.json \
  -o outputs/bimanual_assembly
```

## Example Workflows

### Example 1: Mobile Robot Navigation (Image + Prompt Mode)

```bash
# 1. Analyze your robot image with vision model
python Qwen_instructor/prompt_extender_mobile_robot.py \
  --image Inputimg/ugv/warehouse_navigation.jpg \
  --prompt "navigate around obstacles in warehouse" \
  --verbose

# Output:
# 📷 Analyzing mobile robot image...
# 🧠 Generating physics-based navigation prompt...
# ✅ Saved prompt to: mobile_robot_warehouse_navigation_prompt.txt
# ✅ Saved Cosmos-compatible JSON to: mobile_robot_warehouse_navigation_prompt.json

# 2. Review the generated prompt (optional)
cat mobile_robot_warehouse_navigation_prompt.txt

# 3. Generate video with Cosmos Predict (image2world mode)
python examples/inference.py \
  -i mobile_robot_warehouse_navigation_prompt.json \
  -o outputs/warehouse_nav

# 4. View results in outputs/warehouse_nav/
```

### Example 2: 3 DOF Manipulator (Text-Only Mode)

```bash
# 1. Extend text prompt without image
python Qwen_instructor/prompt_extender_3dof_manipulator_text.py \
  --prompt "pick up blue cylinder and place in assembly station" \
  --verbose

# Output:
# 🧠 Extending prompt with Qwen2.5-VL...
# ✅ Saved prompt to: 3dof_prompt.txt
# ✅ Saved Cosmos-compatible JSON to: 3dof_prompt.json

# 2. Review the extended prompt
cat 3dof_prompt.txt

# 3. Generate video with Cosmos Predict (text2world mode)
python examples/inference.py \
  -i 3dof_prompt.json \
  -o outputs/3dof_manipulation

# 4. View results in outputs/3dof_manipulation/
```

## Customization

### Adding Custom Guidance

**Image + Prompt Mode** - Use `--prompt` to guide vision analysis:

```bash
# 3 DOF with precision requirements
python prompt_extender_3dof_manipulator.py \
  --image assembly.jpg \
  --prompt "extremely slow and precise motion for delicate parts"

# Mobile robot with terrain specifics
python prompt_extender_mobile_robot.py \
  --image outdoor.jpg \
  --prompt "rough terrain with rocks and slopes, reduce speed"

# Bimanual with coordination mode
python prompt_extender_bimanual_ur3.py \
  --image dual_grasp.jpg \
  --prompt "synchronized mirror motion for symmetric assembly"
```

**Text-Only Mode** - Provide detailed task description:

```bash
# 3 DOF with specific object details
python prompt_extender_3dof_manipulator_text.py \
  --prompt "pick up small red cube from left bin, move slowly 30cm right, place gently in assembly fixture"

# Mobile robot with navigation specifics
python prompt_extender_mobile_robot_text.py \
  --prompt "start at warehouse entrance, navigate straight 5 meters at 0.4 m/s, turn right 90 degrees, stop at loading dock"

# Bimanual with detailed coordination
python prompt_extender_bimanual_ur3_text.py \
  --prompt "left arm grasps circuit board and holds steady while right arm positions connector and presses firmly"
```

### Adjusting Token Length
For more detailed prompts, increase max tokens:

```bash
# Image + Prompt mode
python prompt_extender_bimanual_ur3.py \
  --image complex_task.jpg \
  --max-tokens 700

# Text-Only mode
python prompt_extender_mobile_robot_text.py \
  --prompt "complex navigation task" \
  --max-tokens 650
```

## Understanding the Negative Prompts

Each extender includes robot-specific negative prompts to avoid:

**3 DOF Manipulator**:
- 6 DOF motion
- Unrealistic speed
- Workspace violations
- Gripper slipping

**Mobile Robot**:
- Flying/hovering
- Wheels not touching ground
- Instant rotation
- Passing through walls

**Bimanual UR3**:
- Arm collision
- Over-extension beyond reach
- Poor synchronization
- Unrealistic joint angles

## Tips for Best Results

### Image Quality
- Use well-lit images showing the full robot
- Include workspace and objects to manipulate
- Clear view of end-effectors/grippers
- Show environmental context

### Prompt Engineering
- Be specific about the desired task
- Mention speed requirements if critical
- Specify coordination mode for bimanual tasks
- Include safety constraints if relevant

### Cosmos Inference Settings
- `guidance: 7` - Good balance (default)
- `seed: 42` - Reproducibility (change for variation)
- `inference_type: image2world` - Generate from image (can use text2world or video2world)

## Troubleshooting

### Model Loading Issues
```bash
# Ensure model is downloaded
python download_qwen_instructor.py

# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

### Out of Memory
```bash
# Use CPU instead of GPU
python prompt_extender_mobile_robot.py --image robot.jpg --device cpu

# Reduce max tokens
python prompt_extender_mobile_robot.py --image robot.jpg --max-tokens 500
```

### Generated Prompt Not Detailed Enough
```bash
# Increase token limit
--max-tokens 1000

# Add more specific guidance
--prompt "focus on joint-by-joint motion sequence with timing"
```

## Architecture Deep Dive

### Cosmos Predict 2.5 Architecture

**Cosmos Predict 2.5** is built on:
1. **Flow Matching**: Continuous normalizing flow for video generation
2. **Multimodal Input**: Processes text (via Cosmos-Reason VLM), images, and videos
3. **Physics-Aware Training**: Trained on physical AI datasets including robotics
4. **Context Parallelism**: Distributes video generation across multiple GPUs

**Inference Modes**:
- **Text2World**: Generate video from text prompt only
- **Image2World**: Generate video from image + text prompt (most common for robotics)
- **Video2World**: Continue video from existing video + text prompt

**Model Sizes**:
- 2B parameters (available)
- 14B parameters (coming soon)

### Prompt Extender Architecture

Each specialized extender follows this architecture:

```
Input Image → Qwen2.5-VL Vision Encoder
                     ↓
        Visual Feature Extraction
                     ↓
        Robot-Specific System Prompt + Task Analysis Prompt
                     ↓
        Qwen2.5-VL Language Generator
                     ↓
        Structured Prompt with:
        - Physical Setup
        - Camera State
        - Action Vector
        - Physics Constraints
        - Robot-Specific Constraints
                     ↓
        Post-Processing & Formatting
                     ↓
        Output: TXT + JSON for Cosmos
```

### Why Specialized Extenders?

Generic prompt extenders don't understand:
- **Robot-specific kinematics**: 3 DOF vs 6 DOF, wheel types, joint limits
- **Task-appropriate motion**: Pick-and-place vs navigation vs coordinated manipulation
- **Physics constraints**: Workspace limits, payload capacity, collision zones
- **Domain terminology**: Joint angles, TCP, differential drive, turn radius

Specialized extenders inject this domain knowledge into the vision-language model's analysis, resulting in **physically plausible and robot-appropriate** prompts.

## Advanced Usage

### Batch Processing
```bash
# Process multiple images
for img in Inputimg/ugv/*.jpg; do
  python prompt_extender_mobile_robot.py --image "$img"
done

# Run all generated prompts through Cosmos
python examples/inference.py -i mobile_robot_*_prompt.json -o outputs/batch_ugv
```

### Integration with Post-Training
After generating videos, you can use them for post-training Cosmos on your specific robot:

```bash
# Organize outputs into dataset
# Then follow Cosmos post-training guide:
# docs/post-training_video2world_cosmos_nemo_assets.md
```

### Custom Robot Types
To create your own specialized extender:
1. Copy one of the existing extenders
2. Modify the `system_prompt` with your robot's specifications
3. Update constraint sections
4. Adjust negative prompts

## References

- [Cosmos Predict 2.5 Repository](https://github.com/nvidia-cosmos/cosmos-predict2.5)
- [Cosmos Inference Guide](../docs/inference.md)
- [Cosmos Post-Training Guide](../docs/post-training.md)
- [UR3 Robot Specifications](https://www.universal-robots.com/products/ur3-robot/)
- [Qwen2.5-VL Model](https://huggingface.co/Qwen/Qwen2.5-VL)

## License

These prompt extenders follow the same license as Cosmos Predict 2.5:
- Source code: Apache 2.0 License
- Generated prompts: No restrictions, use as needed for Cosmos inference

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review Cosmos documentation in `docs/`
3. Open an issue on the Cosmos GitHub repository

---

**Created for Cosmos Predict 2.5 - Physics-Based World Foundation Models for Robotics**
