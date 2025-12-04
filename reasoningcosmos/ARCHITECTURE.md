# Architecture Overview - Reasoning Cosmos

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       USER INTERFACE LAYER                          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Interactive CLI (interactive_cosmos_pipeline.py)             │  │
│  │  • Step-by-step wizard                                        │  │
│  │  • Colorized terminal output                                  │  │
│  │  • Input validation                                           │  │
│  │  • Progress feedback                                          │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Batch Processor (batch_cosmos_pipeline.py)                   │  │
│  │  • Directory scanning                                         │  │
│  │  • CSV task processing                                        │  │
│  │  • Parallel-ready                                             │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    ROBOT INTELLIGENCE LAYER                         │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  3 DOF Module    │  │  Mobile Robot    │  │  Bimanual UR3    │  │
│  │  ─────────────   │  │  ─────────────   │  │  ─────────────   │  │
│  │  • SCARA        │  │  • Differential  │  │  • Dual-arm      │  │
│  │  • Delta        │  │  • 4-wheel       │  │  • Coordination  │  │
│  │  • Cartesian    │  │  • Tracked       │  │  • Collision     │  │
│  │  • Pick-place   │  │  • Navigation    │  │  • Handoff       │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│            ↓                      ↓                      ↓           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │         Specialized System Prompts & Constraints            │   │
│  │  • Kinematics      • Physics Rules    • Motion Patterns     │   │
│  │  • Joint Limits    • Traction Models  • Safety Constraints  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    VISION-LANGUAGE MODEL LAYER                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Qwen2.5-VL (7B)                          │   │
│  │  ┌─────────────────────┐      ┌──────────────────────┐     │   │
│  │  │  Vision Encoder     │      │  Language Generator  │     │   │
│  │  │  ───────────────    │      │  ──────────────────  │     │   │
│  │  │  • Image analysis   │  →   │  • Prompt synthesis  │     │   │
│  │  │  • Object detection │      │  • Physics reasoning │     │   │
│  │  │  • Scene understanding     │  • Structure formatting    │   │
│  │  └─────────────────────┘      └──────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  INPUT: Image + "pick up apple"                                      │
│  OUTPUT: Detailed physics-based prompt with:                         │
│    [PHYSICAL SETUP] [CAMERA STATE] [ACTION VECTOR] [CONSTRAINTS]    │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      PROMPT GENERATION LAYER                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Enhanced Prompt Structure                                  │   │
│  │  ══════════════════════════                                 │   │
│  │  • [PHYSICAL SETUP]: Scene description, robot specs         │   │
│  │  • [CAMERA STATE]: Position, motion, velocity               │   │
│  │  • [ACTION VECTOR]: Trajectory, motion profile              │   │
│  │  • [PHYSICS CONSTRAINTS]: Gravity, friction, momentum       │   │
│  │  • [ROBOT CONSTRAINTS]: Joint limits, workspace bounds      │   │
│  │  • [VISUAL QUALITY]: Lighting, motion blur, resolution      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  JSON Configuration                                         │   │
│  │  ══════════════════                                         │   │
│  │  {                                                          │   │
│  │    "name": "cosmos_2_ugv_navigation",                       │   │
│  │    "inference_type": "image2world",                         │   │
│  │    "input_path": "/path/to/image.jpg",                      │   │
│  │    "prompt": "<enhanced_prompt>",                           │   │
│  │    "negative_prompt": "<robot_specific>",                   │   │
│  │    "num_output_frames": 77,                                 │   │
│  │    "guidance": 7,                                           │   │
│  │    "seed": 42,                                              │   │
│  │    ...                                                      │   │
│  │  }                                                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   COSMOS PREDICT 2.5 LAYER                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  World Foundation Model (2B/14B)                            │   │
│  │  ════════════════════════════════                           │   │
│  │                                                             │   │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   │   │
│  │  │  Text Enc    │   │ Flow Model   │   │  VAE Decoder │   │   │
│  │  │  (Reason1)   │→  │  (Diffusion) │→  │  (Video)     │   │   │
│  │  └──────────────┘   └──────────────┘   └──────────────┘   │   │
│  │         ↓                   ↓                    ↓         │   │
│  │    Text Features    Physics Simulation    Video Frames    │   │
│  │                                                             │   │
│  │  Key Features:                                              │   │
│  │  • Flow-based generation for smooth motion                 │   │
│  │  • Physics-aware training on robotics data                 │   │
│  │  • Multi-modal conditioning (text + image + video)         │   │
│  │  • Context parallelism for multi-GPU inference             │   │
│  │  • Autoregressive mode for long videos                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         OUTPUT LAYER                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Generated Video (MP4)                                      │   │
│  │  • Physically realistic robot motion                        │   │
│  │  • Proper ground contact / kinematics                       │   │
│  │  • Smooth trajectories                                      │   │
│  │  • Collision-aware                                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Metadata & Logs                                            │   │
│  │  • Generation parameters                                    │   │
│  │  • Timing information                                       │   │
│  │  • Model version                                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Example

### Example: Mobile Robot Navigation

```
┌──────────────────────────────────────────────────────────────┐
│ USER INPUT                                                   │
├──────────────────────────────────────────────────────────────┤
│ Robot Type: Mobile Robot (UGV)                              │
│ Image: Inputimg/ugv/warehouse.jpg                           │
│ Prompt: "navigate forward and turn left around box"         │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ VISION ANALYSIS (Qwen2.5-VL)                                │
├──────────────────────────────────────────────────────────────┤
│ Detected:                                                    │
│ • Robot: 4-wheeled differential drive UGV                   │
│ • Environment: Indoor warehouse, smooth concrete floor      │
│ • Obstacles: Cardboard box at 3m, shelves in background     │
│ • Lighting: Overhead fluorescent, even illumination         │
│ • Camera: External static view, eye-level, 3m distance      │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ ROBOT INTELLIGENCE (Mobile Robot Module)                    │
├──────────────────────────────────────────────────────────────┤
│ Applied Constraints:                                         │
│ • Planar motion only (wheels on ground)                     │
│ • Turn radius based on wheelbase (~0.5m)                    │
│ • Max velocity: 1.5 m/s                                     │
│ • Acceleration profile: 0.5 m/s²                            │
│ • Collision buffer: 0.3m from obstacles                     │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ ENHANCED PROMPT GENERATION                                   │
├──────────────────────────────────────────────────────────────┤
│ [PHYSICAL SETUP]:                                            │
│ A 4-wheeled differential drive UGV robot with dimensions    │
│ 0.6m length, 0.4m width, operating on smooth concrete       │
│ floor in an indoor warehouse. Cardboard box obstacle at     │
│ 3m forward and 1m left of robot's starting position...      │
│                                                              │
│ [CAMERA STATE]:                                              │
│ STATIC FIXED external camera positioned at eye-level        │
│ (1.5m height), 3m from robot, viewing angle 30° downward... │
│                                                              │
│ [ACTION VECTOR]:                                             │
│ Phase 1 (0-2s): Robot accelerates from rest to 1.0 m/s     │
│ Phase 2 (2-5s): Maintains velocity moving forward 3m       │
│ Phase 3 (5-7s): Decelerates to 0.5 m/s for turn            │
│ Phase 4 (7-9s): Executes 90° left turn (0.5m radius)       │
│ Phase 5 (9-10s): Resumes forward motion past obstacle...    │
│                                                              │
│ [PHYSICS CONSTRAINTS]:                                       │
│ • Gravity: 9.81 m/s², robot remains on ground plane        │
│ • Wheel friction coefficient: 0.7 on concrete              │
│ • No wheel slip during acceleration/deceleration           │
│ • Turn dynamics respect differential drive kinematics...   │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ COSMOS INFERENCE                                             │
├──────────────────────────────────────────────────────────────┤
│ • Encode prompt with Cosmos-Reason1 VLM                     │
│ • Condition on input image                                  │
│ • Generate 77 frames via flow matching                      │
│ • Decode to 432x768 video                                   │
│ • Duration: ~5.5 seconds at 14 FPS                          │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ OUTPUT VIDEO                                                 │
├──────────────────────────────────────────────────────────────┤
│ ✓ Robot accelerates smoothly from stationary              │
│ ✓ Wheels rotate synchronized with forward motion           │
│ ✓ Robot approaches box with deceleration                   │
│ ✓ Executes realistic left turn (proper radius)             │
│ ✓ Maintains ground contact throughout                      │
│ ✓ Background remains static (camera fixed)                 │
│ ✓ Lighting consistent throughout motion                    │
└──────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. Interactive Interface
- **Purpose**: User-friendly CLI for single-image workflows
- **Technology**: Python CLI with colored output
- **Features**: Step-by-step wizard, input validation, progress tracking

### 2. Batch Processor
- **Purpose**: Process multiple images efficiently
- **Technology**: Python subprocess management
- **Features**: Directory scanning, CSV parsing, parallel-ready

### 3. Robot Modules (3 Specialized Prompt Extenders)
- **Purpose**: Inject domain-specific robotics knowledge
- **Technology**: Specialized system prompts for Qwen2.5-VL
- **Features**: Kinematics, physics constraints, motion planning

### 4. Vision-Language Model (Qwen2.5-VL)
- **Purpose**: Understand images and generate structured prompts
- **Technology**: 7B parameter multimodal transformer
- **Features**: Image encoding, text generation, task understanding

### 5. Cosmos Predict 2.5
- **Purpose**: Generate physics-based videos
- **Technology**: Flow-based generative model (2B/14B parameters)
- **Features**: Text/image/video conditioning, physics simulation

## Design Principles

### 1. Separation of Concerns
- **UI Layer**: User interaction and input validation
- **Intelligence Layer**: Robot-specific knowledge
- **Vision Layer**: Image understanding
- **Generation Layer**: Video synthesis

### 2. Modularity
- Each robot type is a separate module
- Easy to add new robot types
- Prompt extenders are independent scripts

### 3. Progressive Enhancement
- Simple mode: Just image + text → video
- Advanced mode: Full control over generation parameters
- Batch mode: Automated processing at scale

### 4. Robustness
- Input validation at every step
- Clear error messages
- Graceful degradation
- Resume capability

## Performance Considerations

### Inference Time
- **Prompt Generation**: ~10-30 seconds (Qwen2.5-VL on GPU)
- **Video Generation**: ~2-5 minutes per 77-frame video (Cosmos on single GPU)
- **Total Pipeline**: ~3-6 minutes per video

### Memory Requirements
- **Qwen2.5-VL**: ~14 GB VRAM (FP16)
- **Cosmos 2B**: ~8 GB VRAM
- **Combined**: Recommend 24 GB VRAM or sequential processing

### Optimization Strategies
1. **Multi-GPU**: Use torchrun for parallel Cosmos inference
2. **Batch Processing**: Amortize model loading across multiple images
3. **CPU Fallback**: Use CPU for Qwen if GPU memory limited
4. **Caching**: Reuse prompt extender outputs

## Extension Points

### Add New Robot Type
1. Create new prompt extender script
2. Define robot-specific constraints
3. Add to robot_modes dictionary
4. Update documentation

### Custom Post-Processing
1. Hook into video output stage
2. Add filters, annotations, or analysis
3. Save additional metadata

### Integration with Training Pipeline
1. Generate synthetic training data
2. Use outputs for Cosmos post-training
3. Create domain-specific datasets

## Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│ Python 3.10+                                            │
│ ├── PyTorch 2.x (Deep learning framework)              │
│ ├── Transformers (Hugging Face)                        │
│ ├── Qwen2.5-VL (Vision-language model)                 │
│ ├── Pillow (Image processing)                          │
│ └── Subprocess (Process management)                    │
│                                                         │
│ Cosmos Predict 2.5                                      │
│ ├── Diffusers (Flow-based generation)                  │
│ ├── Accelerate (Multi-GPU support)                     │
│ ├── NeMo (Training framework)                          │
│ └── Custom modules                                     │
└─────────────────────────────────────────────────────────┘
```

## Future Enhancements

### Planned
- [ ] Web-based GUI interface
- [ ] Real-time video preview during generation
- [ ] Multi-robot coordination scenarios
- [ ] Integration with robot simulators (Gazebo, Isaac)
- [ ] Automated quality assessment

### Research Directions
- [ ] Few-shot learning for new robot types
- [ ] Closed-loop refinement (generate → evaluate → refine)
- [ ] Multi-view consistent generation
- [ ] Longer videos with temporal consistency

---

**Architecture designed for extensibility, performance, and ease of use**
