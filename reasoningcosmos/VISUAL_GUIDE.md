# 📸 Visual Guide - Reasoning Cosmos

## What You'll See When Running

### Starting the Interactive Pipeline

```bash
$ python reasoningcosmos/interactive_cosmos_pipeline.py
```

### Screen Output:

```
======================================================================
   🎬 INTERACTIVE COSMOS PIPELINE - Robotics Video Generation
======================================================================

Powered by: Qwen2.5-VL + Cosmos Predict 2.5
Simple Input → Intelligent Analysis → Physics-Based Video

Select Robot Type:

  [1] 🦾 3 DOF Manipulator
      → SCARA, delta, cartesian robots for pick-and-place

  [2] 🤖 Mobile Robot (UGV)
      → Wheeled/tracked robots for navigation

  [3] 🦿 Bimanual UR3
      → Dual-arm coordination and manipulation

Enter choice [1-3]: 2

✓ Selected: 🤖 Mobile Robot (UGV)

Image Input:
Enter image path (or drag & drop): Inputimg/4.jpg
✓ Image found: /home/humanoid/Downloads/cosmos-predict2.5/Inputimg/4.jpg

Task Description:
Enter a simple, natural language description of what the robot should do.
Examples:
  • 'pick up the apple using right hand'
  • 'navigate forward and turn left to avoid obstacle'
  • 'both arms lift the box together'

Your prompt: pivot around and drive toward camera
✓ Prompt received

Advanced Settings (Optional):
Configure advanced settings? [y/N]: y

Press Enter to use default values in [brackets]

Number of output frames [77]: 77
Random seed [42]: 42
Guidance scale [7]: 7
Resolution (height,width) [432,768]: 432,768
Enable autoregressive mode? [Y/n]: Y

======================================================================
Processing...
======================================================================
Running Mobile Robot (UGV) Analysis...
🧠 Analyzing image with Qwen2.5-VL...

Loading Qwen2.5-VL for mobile robot analysis...
✅ Model loaded successfully for mobile robot tasks!
📷 Analyzing mobile robot image...
🧠 Generating physics-based navigation prompt...

✓ Prompt generation complete!
  📄 Text prompt: cosmos_2_4_prompt.txt
  📋 JSON config: cosmos_2_4_prompt.json
✓ Configuration updated

======================================================================
Configuration Summary
======================================================================
Name: mobile_robot_4
Type: image2world
Frames: 77
Resolution: 432,768
Guidance: 7
Seed: 42
Autoregressive: True

Enhanced Prompt Preview:
[PHYSICAL SETUP]: A grey wheeled UGV robot with differential drive
configuration operates on office carpet. The robot measures approximately
0.5m in length with four wheels providing stable ground contact...

======================================================================

Generate video now? [Y/n]: y

Running Cosmos Inference...
🎬 Generating video (this may take several minutes)...

Command: python examples/inference.py -i cosmos_2_4_prompt.json -o cosmos_2_4_video --inference-type image2world

[Cosmos Predict 2.5 output...]
Loading model...
Processing frames 1/77...
Processing frames 10/77...
...
Processing frames 77/77...
Encoding video...

✓ Video generation complete!
📁 Output directory: reasoningcosmos/outputs/cosmos_2_4_video
🎥 Generated videos:
   cosmos_2_4_video/output.mp4

======================================================================
Pipeline Complete!
======================================================================

🎉 SUCCESS! Video generated successfully!
```

## File Structure After Running

```
reasoningcosmos/
└── outputs/
    ├── cosmos_2_4_prompt.txt              # Human-readable prompt
    ├── cosmos_2_4_prompt.json             # Cosmos config
    └── cosmos_2_4_video/                  # Video output
        ├── output.mp4                     # Final video!
        └── metadata.json                  # Generation info
```

## What the Generated Prompt Looks Like

### Your Simple Input:
```
"pivot around and drive toward camera"
```

### What Qwen Generates:
```
[PHYSICAL SETUP]:
A grey wheeled UGV (Unmanned Ground Vehicle) with differential drive
configuration operates on office carpet in an indoor environment. The
robot has a rectangular chassis measuring approximately 0.5m length ×
0.4m width × 0.3m height, with four independently actuated wheels
(diameter ~0.15m). The office environment features beige walls,
fluorescent ceiling lighting providing even illumination at ~500 lux,
and medium-pile grey carpet flooring (friction coefficient μ ≈ 0.7).

[CAMERA STATE]:
STATIC FIXED external camera positioned at floor level (height: 0.2m)
approximately 3 meters from the robot's starting position. Camera angle:
horizontal view (0° elevation), facing the robot's initial orientation.
CAMERA VELOCITY = 0 m/s (completely stationary). Background elements
(walls, furniture, floor texture) remain FROZEN throughout the sequence
as camera is non-moving.

[ACTION VECTOR - MOBILE ROBOT SPECIFIC]:
Starting Position: Robot at origin (0, 0, 0) facing +Y direction
Target Position: Robot approaches camera position along -Y axis

Phase 1 (t=0.0-1.5s): ROTATION IN PLACE
  • Robot performs zero-radius turn (differential drive capability)
  • Left wheels rotate backward, right wheels rotate forward
  • Angular velocity: 120°/s (smooth profile)
  • Total rotation: 180° to face -Y direction (toward camera)
  • Robot remains at origin position during rotation

Phase 2 (t=1.5-2.5s): ACCELERATION
  • Both wheels accelerate forward synchronously
  • Linear acceleration: 0.5 m/s²
  • Speed increases from 0 → 0.5 m/s
  • Distance traveled: 0.25m

Phase 3 (t=2.5-7.0s): STEADY APPROACH
  • Constant velocity: 0.5 m/s toward camera
  • Wheels rotate at synchronized speed
  • Distance traveled: 2.25m
  • Robot grows larger in frame as distance closes

Phase 4 (t=7.0-8.0s): DECELERATION
  • Linear deceleration: -0.5 m/s²
  • Speed decreases from 0.5 m/s → 0 m/s
  • Final position: 0.5m from camera
  • Robot stops smoothly

[PHYSICS CONSTRAINTS]:
• Gravity: g = 9.81 m/s² acting downward, robot remains on ground plane
• Ground Contact: All four wheels maintain continuous surface contact
• Wheel Dynamics: Wheel rotation speed synchronized with linear velocity
  (no slip condition: v = ω × r)
• Friction: Carpet provides adequate traction (μ = 0.7), no wheel slip
• Momentum: Robot mass (~15 kg) affects acceleration/deceleration profiles
• Collision: None expected, robot stays within free space
• Stability: Low center of gravity (0.15m) prevents tipping

[GROUND CONTACT & LOCOMOTION]:
• Differential Drive Kinematics: Independent left/right wheel control
• Zero-radius turning: Can rotate in place by counter-rotating wheels
• Wheel contact patches deform carpet slightly (~2mm compression)
• No airborne phase: Robot maintains ground contact throughout
• Realistic wheel rotation: Angular velocity visible, synchronized with motion
• Carpet texture interaction: Slight wheel-carpet friction effects

[ENVIRONMENTAL INTERACTION]:
• Perspective: Camera remains fixed, robot approaches and grows in frame
• Relative motion: Background stationary, robot moves relative to frame
• Lighting: Overhead fluorescent lights create subtle shadows beneath robot
• Depth cues: Robot size increases as distance decreases (correct parallax)
• Floor texture: Carpet pile direction and texture remain consistent

[VISUAL QUALITY FOR MOBILE ROBOTICS]:
• Camera stabilization: Fixed camera, no shake or drift
• Motion blur: Minimal during motion, sharp when stationary
• Depth of field: Entire scene in focus (small aperture, ~f/8)
• Frame rate: 30 FPS for smooth motion visualization
• Lighting: Uniform illumination, no harsh shadows
• Resolution: 768×432 (16:9 aspect ratio)
• Sharpness: Clear view of robot details and wheels
```

### Generated Negative Prompt:
```
flying robot, hovering, aerial drone, floating above ground, wheels not
touching floor, sliding without wheel rotation, instant rotation,
teleportation, passing through walls, unrealistic speed, jerky motion,
robot tipping over unrealistically, wheels spinning without traction,
background not moving correctly with robot motion, camera perspective
errors, motion blur on stationary objects, robot morphing or changing
shape, unstable camera shake, poor lighting, out of focus
```

## Input vs Output Comparison

```
┌─────────────────────────────────────────────────────────────┐
│ YOUR INPUT (Simple)                                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Image: [Photo of grey UGV on carpet]                       │
│                                                             │
│ Prompt: "pivot around and drive toward camera"             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓↓↓
            ━━━━━ AUTOMATIC ANALYSIS ━━━━━
                          ↓↓↓
┌─────────────────────────────────────────────────────────────┐
│ SYSTEM OUTPUT (Detailed & Physics-Based)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ✓ Robot identified: Differential drive UGV                 │
│ ✓ Environment: Indoor office, carpet floor                 │
│ ✓ Dimensions: 0.5m × 0.4m × 0.3m, ~15kg mass              │
│ ✓ Motion plan: 180° rotation + 3m forward approach         │
│ ✓ Physics: Gravity, friction, wheel dynamics               │
│ ✓ Camera: Fixed at floor level, 3m distance                │
│ ✓ Timing: 8 seconds total, 4 phases                        │
│ ✓ Visual quality: 30 FPS, proper depth of field            │
│                                                             │
│ → Generated 77-frame video with realistic motion!          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Batch Processing Example

### Create CSV File:
```csv
image_path,prompt
Inputimg/ugv/scene1.jpg,navigate forward slowly
Inputimg/ugv/scene2.jpg,turn left 90 degrees
Inputimg/ugv/scene3.jpg,approach the door and stop
```

### Run Batch:
```bash
$ python reasoningcosmos/batch_cosmos_pipeline.py --mode 2 --csv-file tasks.csv
```

### Output:
```
======================================================================
Processing: scene1.jpg
Prompt: navigate forward slowly
======================================================================
✓ Generated: batch_2_scene1_prompt.json

======================================================================
Processing: scene2.jpg
Prompt: turn left 90 degrees
======================================================================
✓ Generated: batch_2_scene2_prompt.json

======================================================================
Processing: scene3.jpg
Prompt: approach the door and stop
======================================================================
✓ Generated: batch_2_scene3_prompt.json

======================================================================
Batch Processing Complete
======================================================================
Successfully processed: 3 images
Output directory: reasoningcosmos/batch_outputs
======================================================================
```

## Color Legend

When you see these colors in the terminal:

- **🟢 Green** = Success, completed action
- **🔵 Blue** = Information, guidance
- **🟡 Yellow** = Warning, attention needed
- **🔴 Red** = Error, action required
- **🟣 Purple** = Headers, section titles
- **🟦 Cyan** = Prompts asking for input

## Tips for Best Experience

### 1. Image Quality
```
✅ GOOD                          ❌ BAD
────────────────────────────────────────────────
• Well-lit scene                 • Dark/shadowy
• Robot fully visible            • Partially obscured
• Clear focus                    • Blurry
• Relevant context               • Cropped too tight
• Natural perspective            • Distorted angle
```

### 2. Prompt Writing
```
✅ GOOD                          ❌ BAD
────────────────────────────────────────────────
• "turn left 90 degrees"         • "turn left-ish"
• "slowly approach table"        • "go to table"
• "pick up red cube"             • "grab that thing"
• "both arms lift box"           • "lift it"
• "navigate around obstacle"     • "avoid stuff"
```

### 3. Settings Adjustment
```
WHEN TO ADJUST:
────────────────────────────────────────────────
Longer videos     → increase num_output_frames (121, 241)
More variation    → change seed (try 10, 25, 100)
Stricter prompt   → increase guidance (8, 9, 10)
More natural      → decrease guidance (5, 6)
Different quality → adjust resolution
```

## What Success Looks Like

After running the pipeline, you should have:

```
✓ Text file with detailed prompt
✓ JSON file ready for Cosmos
✓ MP4 video file showing:
  • Realistic robot motion
  • Proper physics (gravity, ground contact)
  • Smooth trajectories
  • Correct spatial relationships
  • Natural lighting and shadows
  • No floating or teleportation
  • Proper wheel/joint movement
```

## Common Issues & Solutions

### Issue: Prompt too generic
```
Problem: "The robot moves."
Solution: "The robot accelerates forward at 0.5 m/s for 3 meters."
```

### Issue: Motion not smooth
```
Problem: Low guidance or seed mismatch
Solution: Try guidance=8 or different seed
```

### Issue: Robot physics wrong
```
Problem: Wrong robot mode selected
Solution: Double-check mode matches your robot type
```

## Example Session Recording

```
$ python reasoningcosmos/interactive_cosmos_pipeline.py

[Header displayed]

Enter choice [1-3]: 2
✓ Selected: 🤖 Mobile Robot (UGV)

Enter image path: Inputimg/4.jpg
✓ Image found: /home/humanoid/Downloads/cosmos-predict2.5/Inputimg/4.jpg

Your prompt: pivot around and drive toward camera
✓ Prompt received

Configure advanced settings? [y/N]: n

[Processing...]
✓ Prompt generation complete!
✓ Configuration updated

Generate video now? [Y/n]: y

[Cosmos running...]
✓ Video generation complete!

🎉 SUCCESS! Video generated successfully!

Total time: ~4 minutes
Output: cosmos_2_4_video/output.mp4
```

---

## Ready to Start?

```bash
cd /home/humanoid/Downloads/cosmos-predict2.5
python reasoningcosmos/interactive_cosmos_pipeline.py
```

**Select mode 2 (Mobile Robot) and use your existing `Inputimg/4.jpg`!** 🚀
