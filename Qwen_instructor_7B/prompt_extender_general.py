#!/usr/bin/env python3
"""
Qwen2.5-VL-7B Vision-Based General Prompt Extender for Cosmos Predict 2.5
MODE 3: GENERAL IMAGE ANALYZER

This is a general-purpose image analyzer that works with ANY robot or scene.
It uses Qwen2.5-VL-7B to intelligently analyze images and extend user prompts
based on visual context, without being tuned to specific embodiments.

Use this mode when:
- You have a robot image that doesn't fit the specific embodiments
- You want generic, intelligent prompt extension
- You're working with novel robots or scenes

Example usage:
python prompt_extender_general.py --image Inputimg/custom_robot.jpg --prompt "grasp object"
python prompt_extender_general.py --image Inputimg/scene.jpg --prompt "describe motion" --verbose

Prerequisites:
- Qwen2.5-VL-7B-Instruct model in Qwen_instructor_7B/
- Install required packages: pip install torch transformers accelerate pillow
"""

import argparse
import os
import torch
from transformers import Qwen2_5_VLForConditionalGeneration, Qwen2_5_VLProcessor
from PIL import Image
import json
from typing import Optional
import re

# Configuration
# Use 7B model directory
import sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).parent.absolute()
MODEL_DIR = str(SCRIPT_DIR / ".." / "Qwen_instructor_7B")
DEFAULT_MAX_TOKENS = 700  # Slightly higher for general analysis

class QwenGeneralPromptExtender:
    """General-purpose vision-enhanced prompt extension for any robot/scene"""

    def __init__(self, model_path: str = MODEL_DIR, device: Optional[str] = None):
        """Initialize the general prompt extender"""
        self.model_path = model_path

        # Set up device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        print(f"[GENERAL IMAGE ANALYZER MODE] Using device: {self.device}")

        # Load model
        try:
            print(f"Loading Qwen2.5-VL-7B for general image analysis from {model_path}...")
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_path,
                torch_dtype=torch.bfloat16,
                device_map="auto" if self.device.type == "cuda" else None
            )
            self.processor = Qwen2_5_VLProcessor.from_pretrained(model_path)

            if self.device.type == "cpu":
                self.model = self.model.to(self.device)

            print("✅ Model loaded successfully for general image analysis!")

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}\n\nMake sure Qwen2.5-VL-7B model is in {model_path}")

        # General system prompt for any robot/scene
        # Based on official NVIDIA Cosmos 2.5 research (December 2025)
        self.system_prompt = """You are an expert robotics and computer vision engineer specializing in physics-based video generation for NVIDIA Cosmos Predict 2.5.

**YOUR TASK**: Analyze ANY robot or embodiment image and extend the user's prompt into a detailed, cinematic, physics-grounded video generation prompt.

**CRITICAL: Based on Official NVIDIA Cosmos Examples & Research:**

**MODEL UNDERSTANDING:**
- Cosmos-Reason1 VLM text encoder: specialized for physical AI and embodied reasoning
- Trained on diverse robotics datasets: manipulation, navigation, humanoids, AVs, drones
- Understands physics intuitively through chain-of-thought reasoning
- Processes prompts with physical common sense across all embodiment types

**GENERAL ANALYZER EXPERTISE:**
- Handles ANY robot type: humanoids, quadrupeds, manipulators, mobile robots, drones, AVs
- Locomotion: walking, running, crawling, rolling, flying
- Manipulation: grasping, placing, assembly, tool use
- Navigation: obstacle avoidance, path following, terrain traversal
- Hybrid tasks: mobile manipulation, aerial manipulation, etc.

**OFFICIAL PROMPT STRUCTURE (from NVIDIA Cosmos assets & research):**

**[CINEMATIC OPENING]** (Optional, 10-15 words):
- "A high-definition video captures a [robot type]..." OR
- "The scene showcases a [embodiment] [performing task]..." OR
- Start directly with description if brevity needed

**[ROBOT & ENVIRONMENT DESCRIPTION]** (30-50 words):
- Robot identification and appearance
  * **Humanoid**: "A bipedal humanoid robot with metallic frame and articulated joints"
  * **Quadruped**: "A four-legged robotic platform with black carbon fiber body"
  * **Drone**: "An aerial quadcopter with white propeller guards and camera gimbal"
  * **Manipulator**: "A 7-DOF robotic arm with orange joints and parallel gripper"
  * **Mobile**: "A wheeled robot with differential drive and sensor array"
- Colors, materials, distinctive features
- Environment: indoor/outdoor, terrain type, spatial context
- Lighting: natural/artificial, bright/dim, shadows
- Background: walls, furniture, landscape, sky, obstacles

**[SPATIAL & INITIAL STATE]** (20-30 words):
- Starting position and configuration
  * Humanoid: "standing upright with arms at sides"
  * Quadruped: "crouched low with weight distributed across all four legs"
  * Drone: "hovering at 2 meter altitude"
- Nearby objects or landmarks
- Environment layout

**[MOTION DESCRIPTION - CORE]** (50-80 words):
**MOTION QUALITY LANGUAGE** (from official examples):
- "smooth and controlled" / "practiced precision"
- "deliberate motion" / "steady progress"
- "maintains balance" / "coordinated movement"
- "accelerates gradually" / "decelerates smoothly"

**SENSORY DETAILS** (critical for quality):
- **Sound**: Embodiment-appropriate sounds
  * Humanoid: "servo whir," "foot contact sounds"
  * Quadruped: "mechanical leg articulation," "footpad impacts"
  * Drone: "propeller hum," "altitude adjustment buzz"
  * Manipulator: "joint motors," "gripper clicks"
- **Visual**: "casts shadows," "reflects ambient light," "disturbs dust/leaves"
- **Environmental**: Interaction with surfaces, air movement, wake effects

**MOTION SEQUENCE** (adapt to embodiment):
- Initial state and orientation
- Motion description with key measurements when critical:
  * Humanoid: "takes three deliberate steps forward, approximately 1 meter"
  * Quadruped: "traverses rocky terrain with careful foot placement"
  * Drone: "ascends smoothly to 5 meter altitude while maintaining position"
  * Manipulator: "reaches toward target positioned 40cm away"
- Progressive motion: "begins moving," "maintains course," "adjusts trajectory"
- Physics emphasis: ground contact, balance, momentum, aerodynamics

**[TEMPORAL PROGRESSION]** (25-40 words):
- "As the video progresses..." (NVIDIA official pattern)
- "continues its motion," "maintains balance/course"
- "transitions to [next phase]," "completes the [task]"
- Progressive state changes describing motion evolution

**[ENVIRONMENTAL INTERACTION]** (15-25 words):
- Surface/terrain interaction specific to embodiment
  * Ground robots: "maintains contact with floor," "wheels roll smoothly"
  * Legged robots: "footsteps create subtle impacts," "weight shifts visibly"
  * Aerial: "propeller wash disturbs nearby leaves," "maintains stable hover"
- Dynamic elements in environment

**[FINAL STATE]** (10-20 words):
- Closing description
- Final configuration/position
- Task completion or scene resolution

**TOTAL WORD COUNT: 150-220 words** (flexible based on task complexity)
- Simple motion: 100-140 words
- Complex multi-phase: 180-220 words
- DON'T force 280 words if task is straightforward

**KEY PRINCIPLES (from official NVIDIA Cosmos documentation):**

1. **PHYSICAL REALISM PARAMOUNT**: Embodiment-appropriate physics always
   - Ground robots: continuous ground contact, realistic friction
   - Legged: balance maintenance, zero-moment point, foot placement
   - Aerial: thrust dynamics, air resistance, stable flight
   - Manipulators: joint limits, gravity effects, smooth trajectories

2. **CINEMATIC LANGUAGE**: Use videography terms
   - "captures," "showcases," "demonstrates," "reveals"
   - "choreographed precision" / "practiced motion"

3. **MATERIAL & COLOR SPECIFICITY**:
   - Always specify colors and materials
   - Surface properties: matte, glossy, metallic, carbon fiber
   - Environmental textures: concrete, grass, carpet, tile

4. **ENVIRONMENTAL CONTEXT**: Never isolate robot in void
   - Spatial boundaries and surfaces
   - Obstacles and landmarks
   - Lighting and atmospheric conditions

5. **EMBODIMENT-APPROPRIATE LANGUAGE**:
   - Humanoid: "walks," "steps," "reaches," "grasps," "balances"
   - Quadruped: "trots," "paces," "leaps," "crouches," "stabilizes"
   - Wheeled: "rolls," "navigates," "maneuvers," "cruises"
   - Aerial: "hovers," "ascends," "descends," "banks," "maintains altitude"

6. **TEMPORAL CONSISTENCY LANGUAGE**:
   - "gradually," "smoothly," "transitions to"
   - "maintains," "continues," "progresses"
   - Progressive description, NOT rigid time stamps

7. **MOTION QUALITY > VELOCITY NUMBERS**:
   - ✅ "walks with measured steps" / "steady forward progress"
   - ✅ "smooth ascent" / "controlled descent"
   - ❌ "velocity = 0.8 m/s" / "acceleration = 0.3 m/s²"
   - Let Cosmos-Reason1 infer realistic physics

8. **SENSORY IMMERSION**:
   - Sound effects appropriate to embodiment
   - Visual effects: shadows, reflections, environmental disturbance
   - Physical interactions: contact, deformation, wake

**CRITICAL RULES:**
✅ Use cinematic opening for complex tasks
✅ Identify robot type and specify appearance (colors, materials, form)
✅ Include rich environmental context
✅ Add embodiment-appropriate sensory details
✅ Progressive temporal language: "As the video progresses..."
✅ Motion quality descriptors: "smooth," "controlled," "deliberate," "balanced"
✅ Physics appropriate to embodiment type
✅ Describe final state for closure
✅ Flexible word count: 100-220 words based on complexity

❌ Don't over-specify with excessive numerical precision
❌ Don't ignore environmental context
❌ Don't skip sensory details (sound effects especially)
❌ Don't violate embodiment physics (flying ground robots, etc.)
❌ Don't use vague language ("moves around," "goes there")
❌ Don't force long prompts for simple motions

**EMBODIMENT-SPECIFIC GUIDELINES:**

**For HUMANOIDS** (G1, Atlas, Digit, etc.):
- Balance emphasis: "maintains upright posture," "weight shifts naturally"
- Bipedal gait: "walks with alternating leg motion," "steps carefully"
- Arm motion: "swings arms naturally for balance" (if not manipulating)
- Sound: servo whir, foot impacts, mechanical joint sounds

**For QUADRUPEDS** (Spot, ANYmal, Go2, etc.):
- Gait patterns: "trot," "walk," "bound" (appropriate to speed)
- Stability: "maintains stable base," "distributes weight across legs"
- Terrain adaptation: "adjusts foot placement," "navigates uneven surface"
- Sound: mechanical leg articulation, footpad impacts

**For WHEELED/TRACKED MOBILE ROBOTS**:
- Ground contact: "wheels maintain continuous contact," "tracks grip surface"
- Navigation: "maneuvers smoothly," "executes turn with appropriate radius"
- Sound: motor whir, wheel rolling, mechanical drive sounds

**For AERIAL ROBOTS** (Drones, UAVs):
- Flight stability: "maintains steady hover," "adjusts for air currents"
- Altitude changes: "ascends gradually," "descends in controlled manner"
- Orientation: "banks slightly," "rotates smoothly"
- Sound: propeller hum, pitch changes with thrust

**For MANIPULATORS** (Industrial arms, cobots):
- Reach and workspace: stay within physical limits
- End-effector motion: "approaches smoothly," "maintains steady grip"
- Joint coordination: "moves in coordinated fashion"
- Sound: joint motors, gripper actuation, hydraulics

**ADAPTIVE APPROACH**:
- Analyze image to identify embodiment type
- Apply appropriate physics and motion vocabulary
- Include embodiment-specific sensory details
- Ensure realistic constraints for that embodiment

**REFERENCE**: See COSMOS_PROMPTING_RESEARCH.md for full research basis
"""

    def load_and_validate_image(self, image_path: str) -> Image.Image:
        """Load and validate the input image"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        try:
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
        except Exception as e:
            raise ValueError(f"Failed to load image: {e}")

    def enhance_prompt_from_image(self, image_path: str, user_prompt: str,
                                max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
        """
        Analyze general image and generate enhanced Cosmos-style prompt

        Args:
            image_path: Path to any robot/scene image
            user_prompt: User's description of desired motion/action
            max_tokens: Maximum tokens for generation

        Returns:
            Enhanced prompt optimized for Cosmos video generation
        """
        # Load and validate image
        image = self.load_and_validate_image(image_path)

        # Create general analysis prompt
        base_analysis = f"""Analyze this image and extend the user's prompt into a CONCISE Cosmos Predict prompt (<300 words).

**USER PROMPT:** "{user_prompt}"

**YOUR TASK:**
1. Identify what's in the image (robot type, scene, objects, environment)
2. Infer appropriate camera position from the image perspective
3. Extend the user's prompt with specific physics-based motion details
4. Keep it SHORT and ACTION-FOCUSED (<300 words)

**REQUIRED FORMAT:**

[CAMERA STATE]:
STATIC CAMERA: [describe the camera angle you see in the image - e.g., "elevated 45-degree view, 1.2m height" or "side view at table level"]
CAMERA VELOCITY = 0
FOV: [estimate based on image]
Background: FROZEN

[ACTION - Based on user prompt "{user_prompt}"]:
Starting state: [describe current pose/position from image]
Motion sequence:
- t=0-Xs: [specific action with measurements - extend user's intent]
- t=X-Ys: [continue the motion]
Target: [final state]

[PHYSICS]:
- Smooth dynamics and realistic motion
- Gravity and constraints from image
- No instant teleportation
- Controlled velocities

**CRITICAL:** Start with [CAMERA STATE]. Focus on MOTION from user prompt. Under 300 words. Use exact measurements."""

        try:
            # Process image and text inputs
            messages = [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image},
                        {"type": "text", "text": base_analysis}
                    ]
                }
            ]

            # Prepare inputs
            text_prompt = self.processor.apply_chat_template(messages, add_generation_prompt=True)
            inputs = self.processor(
                text=[text_prompt],
                images=[image],
                padding=True,
                return_tensors="pt"
            )
            inputs = inputs.to(self.device)

            # Generate
            with torch.no_grad():
                output_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    do_sample=False
                )

            # Decode
            generated_ids = [
                output_ids[len(input_ids):]
                for input_ids, output_ids in zip(inputs.input_ids, output_ids)
            ]
            response = self.processor.batch_decode(
                generated_ids,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )[0]

            return self.clean_response(response)

        except Exception as e:
            raise RuntimeError(f"Failed to generate prompt from image: {e}")

    def clean_response(self, response: str) -> str:
        """Clean and format the model's response"""
        response = response.strip()
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        if response.startswith("'") and response.endswith("'"):
            response = response[1:-1]

        # Normalize whitespace
        response = re.sub(r'\s+', ' ', response)

        return response


def main():
    parser = argparse.ArgumentParser(
        description="Generate Cosmos Predict prompts from ANY image using Qwen2.5-VL-7B general analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --image Inputimg/custom_robot.jpg --prompt "grasp the object"
  %(prog)s --image Inputimg/scene.jpg --prompt "move forward slowly" --verbose
  %(prog)s --image path/to/image.jpg --prompt "describe motion" -o analysis.txt
        """
    )
    parser.add_argument("--image", "-i", type=str, required=True,
                       help="Path to any robot/scene image")
    parser.add_argument("--prompt", "-p", type=str, required=True,
                       help="User prompt describing desired motion/action")
    parser.add_argument("--output", "-o", type=str,
                       help="Output file to save enhanced prompt (optional)")
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS,
                       help="Maximum tokens for generation")
    parser.add_argument("--device", type=str, choices=['cpu', 'cuda'],
                       help="Device to use (default: auto-detect)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed progress and output")

    args = parser.parse_args()

    # Generate default output filename
    if not args.output and args.image:
        image_basename = os.path.splitext(os.path.basename(args.image))[0]
        args.output = f"general_{image_basename}_prompt.txt"

    if args.verbose:
        print("🤖 Qwen2.5-VL-7B General Image Analyzer")
        print(f"Image: {args.image}")
        print(f"User prompt: {args.prompt}")
        print(f"Output: {args.output}")
        print(f"Max tokens: {args.max_tokens}")
        print("-" * 70)

    try:
        # Initialize the general prompt extender
        extender = QwenGeneralPromptExtender(device=args.device)

        # Analyze image and generate prompt
        if args.verbose:
            print("📷 Analyzing image with general vision model...")
            print(f"🧠 Extending prompt: '{args.prompt}'...")

        enhanced_prompt = extender.enhance_prompt_from_image(
            args.image,
            args.prompt,
            args.max_tokens
        )

        # Display result
        print("\n🎬 Enhanced Prompt (General Analysis - Cosmos Predict):")
        print("=" * 70)
        print(enhanced_prompt)
        print("=" * 70)

        # Save to file if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(enhanced_prompt)
            print(f"\n✅ Saved prompt to: {args.output}")

            # Generate Cosmos-compatible JSON
            json_output = args.output.replace('.txt', '.json')
            image_name = os.path.splitext(os.path.basename(args.image))[0]
            clean_name = re.sub(r'[^\w\-_]', '_', image_name)[:30]

            cosmos_data = {
                "name": f"general_{clean_name}",
                "input_path": os.path.abspath(args.image),
                "prompt": enhanced_prompt,
                "negative_prompt": "unrealistic motion, teleportation, object morphing, floating objects ignoring gravity, instant acceleration, shaky camera, excessive motion blur, poor lighting, out of focus, jerky motion, physics violations, collision through objects",
                "num_output_frames": 77,
                "resolution": "432,768",
                "seed": 42,
                "guidance": 7,
                "inference_type": "image2world"
            }

            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(cosmos_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Saved Cosmos-compatible JSON to: {json_output}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
