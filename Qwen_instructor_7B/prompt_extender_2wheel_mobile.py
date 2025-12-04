#!/usr/bin/env python3
"""
Qwen2.5-VL-7B Vision-Based Prompt Extender for Cosmos Predict 2.5
SPECIALIZED FOR: 2-WHEEL MOBILE ROBOT

This prompt extender is optimized for 2-wheel differential drive mobile robots
used for autonomous navigation, exploration, and material transport.

2-wheel mobile robot characteristics:
- Differential drive locomotion (two powered wheels)
- Planar ground motion with turn-in-place capability
- Typical speed: 0.2-1.0 m/s
- Turn radius: can rotate on spot (zero turning radius)
- Applications: indoor navigation, delivery, exploration

Example usage:
python prompt_extender_2wheel_mobile.py --image Inputimg/2wheel/navigation.jpg
python prompt_extender_2wheel_mobile.py --image Inputimg/2wheel/warehouse_robot.jpg --prompt "navigate and turn"

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
DEFAULT_MAX_TOKENS = 600  # Reduced to target <300 word output (~200-250 words optimal)

class Qwen2WheelMobilePromptExtender:
    """Vision-enhanced prompt extension specialized for 2-wheel differential drive mobile robots"""

    def __init__(self, model_path: str = MODEL_DIR, device: Optional[str] = None):
        """Initialize the 2-wheel mobile robot prompt extender"""
        self.model_path = model_path

        # Set up device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        print(f"[MOBILE ROBOT / UGV MODE] Using device: {self.device}")

        try:
            # Load model and processor
            print(f"Loading Qwen2.5-VL for mobile robot analysis from {model_path}...")
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                device_map="auto" if self.device.type == "cuda" else None,
            ).to(self.device)

            self.processor = Qwen2_5_VLProcessor.from_pretrained(model_path)
            print("✅ Model loaded successfully for mobile robot tasks!")

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}\nMake sure you've run download_qwen_instructor.py first")

        # Specialized system prompt for 2-wheel mobile robot navigation
        # Based on official NVIDIA Cosmos 2.5 research (December 2025)
        self.system_prompt = """You are an expert robotics engineer specializing in 2-wheel differential drive mobile robots and physics-based video generation for NVIDIA Cosmos Predict 2.5.

**CRITICAL: Based on Official NVIDIA Cosmos Examples & Research:**

**MODEL UNDERSTANDING:**
- Cosmos-Reason1 VLM text encoder: specialized for physical AI and embodied reasoning
- Trained on autonomous vehicle datasets and robotics navigation scenarios
- Understands physics intuitively: wheel-ground contact, momentum, turning dynamics
- Processes prompts with spatial reasoning and temporal consistency

**MOBILE ROBOT EXPERTISE:**
- Differential drive, skid-steering, mecanum wheels, tracked vehicles
- Ground contact physics: continuous wheel/track contact, no hovering
- Velocity profiles: smooth acceleration → steady cruise → controlled deceleration
- Turn radius constraints based on wheelbase and drive mechanism
- Navigation in indoor/outdoor environments: offices, warehouses, streets, terrain

**OFFICIAL PROMPT STRUCTURE (from NVIDIA Cosmos assets & research):**

**[CINEMATIC OPENING]** (Optional, 10-15 words):
- "A video captures a mobile robot navigating through..." OR
- "The scene showcases a two-wheeled robot..." OR
- Start directly with robot description if brevity needed

**[ROBOT & ENVIRONMENT DESCRIPTION]** (30-45 words):
- Robot appearance: colors, form factor, wheel/track type
  * Example: "A compact white robot with two large wheels and black sensor array"
  * Example: "A tracked vehicle with olive-green casing and mounted cameras"
- Environment: indoor corridor, warehouse aisle, outdoor path, urban street
- Surface: "smooth concrete floor," "carpeted hallway," "rough terrain," "asphalt road"
- Lighting: "bright overhead lights," "natural sunlight," "dimly lit space"
- Background elements: walls, shelving, landmarks, obstacles

**[SPATIAL CONTEXT]** (15-25 words):
- Starting position and orientation
- Nearby objects or landmarks for spatial grounding
- Path layout: straight corridor, curved path, open space
- Obstacles or dynamic elements if present

**[NAVIGATION DESCRIPTION - CORE]** (50-70 words):
**MOTION QUALITY LANGUAGE** (from official examples):
- "accelerates smoothly" (NOT "accelerates at 0.2 m/s²")
- "maintains steady cruising speed" / "glides steadily"
- "executes a smooth left turn" / "curves gently to the right"
- "comes to a controlled stop" / "decelerates gradually"

**SENSORY DETAILS** (critical for quality):
- **Sound**: "soft motor whir," "wheels rolling," "mechanical hum"
- **Visual**: "casts shadows on the floor," "reflects ambient light"
- **Motion**: "leaves no visible tracks" / "disturbs dust slightly"

**NAVIGATION SEQUENCE**:
- Initial state: robot at rest or in motion
- Motion description with key measurements when critical:
  * "positioned in the center of the corridor"
  * "travels forward approximately 2 meters"
  * "executes a wide turn around the corner"
- Ground contact emphasis: "wheels maintain continuous contact with the carpeted floor"
- Progressive motion: "accelerates smoothly," "maintains course," "reduces speed"

**[TEMPORAL PROGRESSION]** (25-35 words):
- "As the video progresses..." (NVIDIA official pattern)
- "continues forward," "maintains its trajectory"
- "transitions to turning," "completes the navigation"
- Progressive description: "initially stationary" → "in motion" → "approaching destination"

**[ENVIRONMENTAL INTERACTION]** (15-25 words):
- Ground contact: "wheels roll smoothly across the surface"
- Wake/trails if applicable: "leaves subtle tire marks" / "disturbs no debris"
- Dynamic elements: "passes by stationary equipment" / "navigates around obstacles"

**[FINAL STATE]** (10-20 words):
- Stopping position: "comes to rest at the target location"
- Final orientation
- Scene resolution

**TOTAL WORD COUNT: 140-200 words** (flexible based on task complexity)
- Simple straight-line: 100-130 words
- Complex multi-turn navigation: 170-200 words
- DON'T force 250 words if task is simple

**KEY PRINCIPLES (from official NVIDIA Cosmos documentation):**

1. **PHYSICAL REALISM PARAMOUNT**: Ground contact always maintained, realistic acceleration/deceleration, no instant rotation or flying

2. **CINEMATIC LANGUAGE**: Use videography terms
   - "captures," "showcases," "reveals," "follows"
   - "glides," "navigates," "traverses"

3. **SURFACE & MATERIAL SPECIFICITY**:
   - Surface type: concrete, carpet, asphalt, gravel, tile
   - Robot materials: metallic chassis, rubber wheels, plastic casing
   - Colors: specify robot and environment colors

4. **ENVIRONMENTAL CONTEXT**: Never place robot in void
   - Spatial boundaries: walls, corridors, open spaces
   - Landmarks and objects for spatial reference
   - Lighting conditions and shadows

5. **TEMPORAL CONSISTENCY LANGUAGE**:
   - "gradually," "smoothly," "transitions to"
   - "maintains," "continues," "approaches"
   - Progressive description, NOT rigid time stamps

6. **MOTION QUALITY > VELOCITY NUMBERS**:
   - ✅ "accelerates smoothly" / "steady cruising speed"
   - ✅ "wide turn radius" / "tight maneuver"
   - ❌ "accelerates at 0.25 m/s²" / "velocity = 0.8 m/s"
   - Let Cosmos-Reason1 infer realistic navigation physics

7. **SENSORY IMMERSION**:
   - Sound: motor whir, wheels rolling, mechanical sounds
   - Visual: shadows, reflections, motion blur if fast
   - Tactile implied: wheel-ground contact, smooth/rough surface

**CRITICAL RULES:**
✅ Use cinematic opening for complex navigation
✅ Specify surface type and robot appearance (colors, materials)
✅ Include environmental context (walls, landmarks, lighting)
✅ Add sensory details (motor sounds, wheel rolling sounds)
✅ Progressive temporal language: "As the video progresses..."
✅ Motion quality words: "smooth," "steady," "controlled," "gradual"
✅ Ground contact always emphasized
✅ Describe final state for closure
✅ Flexible word count: 100-200 words based on complexity

❌ Don't over-specify with excessive numerical precision
❌ Don't ignore environmental/spatial context
❌ Don't skip sensory details (sound effects especially)
❌ Don't allow floating/hovering (wheels always on ground)
❌ Don't use vague language ("moves forward" - specify distance)
❌ Don't force 250 words for simple straight-line navigation

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

    def enhance_prompt_from_image(self, image_path: str, additional_prompt: str = "",
                                max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
        """
        Analyze 2-wheel mobile robot image and generate enhanced Cosmos-style prompt

        Args:
            image_path: Path to the image file showing 2-wheel mobile robot
            additional_prompt: Optional additional guidance text
            max_tokens: Maximum tokens for generation

        Returns:
            Enhanced prompt optimized for 2-wheel mobile robot video generation
        """
        # Load and validate image
        image = self.load_and_validate_image(image_path)

        # Create 2-wheel mobile robot-specific analysis prompt
        base_analysis = """Analyze this 2-wheel mobile robot image and generate a CONCISE Cosmos Predict prompt (<300 words, aim for 150-250 words).

**CRITICAL INSTRUCTIONS:**
1. Start with [CAMERA STATE] declaration FIRST
2. Focus on NAVIGATION TASK not scene description
3. Use EXACT measurements (meters, m/s, turn radius, seconds)
4. Keep it SHORT and ACTION-FOCUSED

**REQUIRED FORMAT:**

[CAMERA STATE]:
[Choose one:]
- STATIC CAMERA: External fixed at [position - "4m from robot, floor level, frontal view"]
- ONBOARD CAMERA: Mounted on robot, moves with robot
CAMERA VELOCITY = [0 if static, "moves with robot" if onboard]
Background: [FROZEN if static, "moves relative to robot" if onboard]

[ACTION - NAVIGATION]:
Starting position: [robot pose and orientation]
Navigation sequence with EXACT measurements:
- Phase 1 (t=0-2s): "Accelerates from rest to [speed] m/s"
- Phase 2 (t=2-5s): "Cruises at steady [speed] m/s, travels [distance] meters [direction]"
- Phase 3 (t=5-7s): [If turning: "Executes [direction] turn, radius [X]m, reduces to [speed] m/s"]
- Phase 4 (t=7-8s): "Decelerates smoothly to stop [position]"
Final position: [exact location]

[PHYSICS]:
- Wheels maintain ground contact on [surface type]
- Smooth acceleration: 0 → [speed] m/s over [time]s
- [Drive type]: [turning capability, e.g., "differential drive enables 1.5m turn radius"]
- Friction: [surface] affects traction
- No floating, instant rotation, or teleportation

**Generate a professional, CONCISE navigation prompt following this exact structure. DO NOT exceed 300 words.**"""

        if additional_prompt:
            base_analysis += f"\n\nADDITIONAL NAVIGATION GUIDANCE: {additional_prompt}"

        base_analysis += "\n\nGenerate a detailed, professional prompt for 2-wheel mobile robot video generation, emphasizing physical realism and proper ground locomotion."

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

            # Apply chat template
            text = self.processor.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )

            # Process inputs
            model_inputs = self.processor(
                text=[text],
                images=image,
                return_tensors="pt"
            ).to(self.device)

            # Generate enhanced prompt
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **model_inputs,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.processor.tokenizer.pad_token_id
                )

            # Decode the generated text
            generated_ids = generated_ids[:, model_inputs['input_ids'].shape[1]:]
            enhanced_prompt = self.processor.decode(generated_ids[0], skip_special_tokens=True).strip()

            # Clean up and format the response
            enhanced_prompt = self._clean_and_format_response(enhanced_prompt)

            return enhanced_prompt

        except Exception as e:
            raise RuntimeError(f"Failed to generate 2-wheel mobile robot prompt from image: {e}")

    def _clean_and_format_response(self, response: str) -> str:
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
        description="Generate Cosmos Predict prompts for 2-wheel mobile robots using Qwen2.5-VL-7B vision analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --image Inputimg/ugv/warehouse_bot.jpg
  %(prog)s --image Inputimg/ugv/outdoor_navigation.jpg --prompt "rough terrain traversal"
  %(prog)s --image path/to/robot.jpg -o mobile_robot_analysis.txt --verbose
        """
    )
    parser.add_argument("--image", "-i", type=str, required=True,
                       help="Path to image showing 2-wheel mobile robot")
    parser.add_argument("--prompt", "-p", type=str, default="",
                       help="Optional additional guidance for prompt generation")
    parser.add_argument("--output", "-o", type=str,
                       help="Output file to save enhanced prompt (optional)")
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS,
                       help="Maximum tokens for generation")
    parser.add_argument("--device", type=str, choices=['cpu', 'cuda'],
                       help="Device to use (default: auto-detect)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed progress and output")

    args = parser.parse_args()

    # Generate default output filename from image path
    if not args.output and args.image:
        image_basename = os.path.splitext(os.path.basename(args.image))[0]
        args.output = f"mobile_robot_{image_basename}_prompt.txt"

    if args.verbose:
        print("🤖 Qwen2.5-VL-7B 2-Wheel Mobile Robot Prompt Extender")
        print(f"Image: {args.image}")
        print(f"Additional prompt: {args.prompt}")
        print(f"Output: {args.output}")
        print(f"Max tokens: {args.max_tokens}")
        print("-" * 70)

    try:
        # Initialize the 2-wheel mobile robot prompt extender
        extender = Qwen2WheelMobilePromptExtender(device=args.device)

        # Analyze image and generate prompt
        if args.verbose:
            print("📷 Analyzing 2-wheel mobile robot image...")
            print("🧠 Generating physics-based navigation prompt...")

        enhanced_prompt = extender.enhance_prompt_from_image(
            args.image,
            args.prompt,
            args.max_tokens
        )

        # Display result
        print("\n🎬 Enhanced Prompt for Mobile Robot (Cosmos Predict):")
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
                "name": f"2wheel_mobile_{clean_name}",
                "input_path": os.path.abspath(args.image),
                "prompt": enhanced_prompt,
                "negative_prompt": "flying robot, hovering, aerial drone, floating above ground, wheels not touching floor, sliding without wheel rotation, instant rotation, teleportation, passing through walls, unrealistic speed, jerky motion, robot tipping over unrealistically, wheels spinning without traction, background not moving correctly with robot motion, camera perspective errors, motion blur on stationary objects, robot morphing or changing shape, unstable camera shake, poor lighting, out of focus.",
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
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
