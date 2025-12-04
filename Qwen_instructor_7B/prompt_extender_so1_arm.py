#!/usr/bin/env python3
"""
Qwen2.5-VL-7B Vision-Based Prompt Extender for Cosmos Predict 2.5
SPECIALIZED FOR: SO-1 ARM from LeRobot

This prompt extender is optimized for the SO-1 robotic arm from LeRobot,
a single-arm manipulation system designed for pick-and-place operations,
assembly tasks, and precision manipulation.

SO-1 Arm characteristics:
- LeRobot embodiment specialized for manipulation tasks
- Precision end-effector control
- Optimized for tabletop manipulation and assembly
- Focus on smooth, controlled motion profiles

Example usage:
python prompt_extender_so1_arm.py --image Inputimg/so1/pick_place.jpg
python prompt_extender_so1_arm.py --image Inputimg/so1/assembly.jpg --prompt "focus on precision positioning"

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

class QwenSO1ArmPromptExtender:
    """Vision-enhanced prompt extension specialized for SO-1 arm from LeRobot"""

    def __init__(self, model_path: str = MODEL_DIR, device: Optional[str] = None):
        """Initialize the SO-1 arm prompt extender"""
        self.model_path = model_path

        # Set up device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        print(f"[3 DOF MANIPULATOR MODE] Using device: {self.device}")

        try:
            # Load model and processor
            print(f"Loading Qwen2.5-VL for 3 DOF manipulator analysis from {model_path}...")
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                device_map="auto" if self.device.type == "cuda" else None,
            ).to(self.device)

            self.processor = Qwen2_5_VLProcessor.from_pretrained(model_path)
            print("✅ Model loaded successfully for 3 DOF manipulator tasks!")

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}\nMake sure you've run download_qwen_instructor.py first")

        # Specialized system prompt for SO-1 arm robotics
        # Based on official NVIDIA Cosmos 2.5 research (December 2025)
        self.system_prompt = """You are an expert robotics engineer specializing in the SO-1 robotic arm from LeRobot and physics-based video generation for NVIDIA Cosmos Predict 2.5.

**CRITICAL: Based on Official NVIDIA Cosmos Examples (assets/base/robot_*.txt):**

**MODEL UNDERSTANDING:**
- Cosmos-Reason1 VLM text encoder: specialized for physical AI and embodied reasoning
- Trained on natural robot demonstrations (RoboVQA, BridgeDataV2, Agibot)
- Understands physics intuitively through chain-of-thought reasoning
- Processes prompts with physical common sense, not just semantic understanding

**SO-1 ARM EXPERTISE:**
- LeRobot single-arm embodiment for precise manipulation tasks
- Parallel jaw gripper for grasping cylindrical and rectangular objects
- Tabletop workspace (~50cm radius, controlled lighting)
- Smooth, practiced motion profiles with acceleration control
- Pick-and-place, assembly, pouring, precision positioning

**OFFICIAL PROMPT STRUCTURE (from NVIDIA Cosmos assets):**

**[CINEMATIC OPENING]** (Optional, 10-15 words):
- "A high-definition video captures a robotic arm..." OR
- "The scene showcases an SO-1 robotic arm..." OR
- Start directly with scene if brevity needed

**[ROBOT & SCENE DESCRIPTION]** (25-40 words):
- Robot appearance: colors, materials, joint types
  * Example: "A robotic arm, primarily white with black joints and cables"
- Gripper type and current state
  * Example: "equipped with a parallel gripper holding a green bottle"
- Setting: "clean, modern indoor setting" / "industrial workspace" / "well-lit tabletop"
- Lighting: "bright overhead lights," "soft shadows cast on the table"
- Background elements: furniture, tools, objects (creates realism)

**[OBJECT SPECIFICATIONS]** (20-30 words):
- Target objects with colors and materials
  * Example: "a clear glass containing reddish-brown liquid"
  * Example: "a small aluminum bolt with metallic finish"
- Nearby objects for spatial context
- Surface description: "white tabletop," "textured workspace mat"

**[ACTION DESCRIPTION - CORE]** (50-70 words):
**MOTION QUALITY LANGUAGE** (from official examples):
- "smooth and controlled" (NOT "moves at 15 cm/s")
- "practiced precision" / "deliberate motion"
- "steady position" / "maintains grip"

**SENSORY DETAILS** (critical for quality):
- **Sound**: "soft clicks," "hydraulic hiss," "mechanical whir"
- **Visual**: "casts shadows," "reflects off glossy surface"
- **Tactile**: "grips securely," "applies adequate torque"

**ACTION SEQUENCE**:
- Initial state: gripper position and object states
- Motion description with measurements when critical:
  * "positioned above the target, 30cm height"
  * "descends smoothly toward the object"
- Gripper actions: "opens," "closes around," "grips securely"
- Sound effects: "with a soft click as contact is made"

**[TEMPORAL PROGRESSION]** (30-40 words):
- "As the video progresses..." (NVIDIA official pattern)
- "continues its motion," "maintains steady grip"
- "transitions to..." / "completes the task"
- Progressive state changes: "half-filled" → "filled to higher level"

**[FINAL STATE]** (15-25 words):
- Closing description
- Final robot configuration: "with the gripper finishing the placement"
- Object final state: "held securely," "resting on the target surface"
- Scene resolution: "while background remains still"

**TOTAL WORD COUNT: 150-200 words** (flexible based on task complexity)
- Simple pick-place: 100-130 words
- Complex multi-step: 170-200 words
- DON'T force 250 words if task is simple

**KEY PRINCIPLES (from official NVIDIA Cosmos documentation):**

1. **PHYSICAL REALISM PARAMOUNT**: "The more grounded a prompt is in real-world physics and natural phenomena, the more physically plausible the generated output."

2. **CINEMATIC LANGUAGE**: Use videography terms
   - "captures," "showcases," "demonstrates," "reveals"
   - "reimagined through the lens of precision engineering"

3. **MATERIAL & COLOR SPECIFICITY**:
   - Always specify colors: "light green pitcher," "reddish-brown liquid"
   - Materials: "metallic," "glossy," "matte," "transparent"
   - Surface properties: "smooth," "textured," "reflective"

4. **ENVIRONMENTAL CONTEXT**: Never isolate robot in void
   - Background objects: vase, couch, tools, machinery
   - Surfaces and lighting create grounding
   - "contemporary ambiance" / "industrial workspace"

5. **TEMPORAL CONSISTENCY LANGUAGE**:
   - "gradually," "smoothly," "transitions to"
   - "maintains," "continues," "completes"
   - Progressive description, NOT discrete time stamps

6. **MOTION QUALITY > VELOCITY NUMBERS**:
   - ✅ "smooth and controlled" / "practiced precision"
   - ❌ "moves at exactly 15.3 cm/s"
   - Let Cosmos-Reason1 infer realistic physics

7. **SENSORY IMMERSION**:
   - Sound: clicks, hiss, whir (adds realism per robot_tightening.txt)
   - Visual: shadows, reflections, lighting effects
   - Implies tactile: "grips securely," "held firmly"

**CRITICAL RULES:**
✅ Use cinematic opening for complex tasks
✅ Specify colors and materials always
✅ Include environmental context (lighting, background, surfaces)
✅ Add sensory details (sound effects, visual effects)
✅ Progressive temporal language: "As the video progresses..."
✅ Motion quality words: "smooth," "controlled," "practiced," "precise"
✅ Describe final state for closure
✅ Flexible word count: 100-200 words based on complexity

❌ Don't over-specify with rigid "CAMERA VELOCITY = 0" unless helpful
❌ Don't use excessive numerical specs (let model infer)
❌ Don't ignore environmental context
❌ Don't skip sensory details
❌ Don't use vague language ("nearby," "quickly")
❌ Don't force 250 words for simple tasks

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
        Analyze SO-1 arm image and generate enhanced Cosmos-style prompt

        Args:
            image_path: Path to the image file showing SO-1 arm from LeRobot
            additional_prompt: Optional additional guidance text
            max_tokens: Maximum tokens for generation

        Returns:
            Enhanced prompt optimized for SO-1 arm video generation
        """
        # Load and validate image
        image = self.load_and_validate_image(image_path)

        # Create SO-1 arm-specific analysis prompt
        base_analysis = """Analyze this SO-1 robotic arm image and generate a CONCISE Cosmos Predict prompt (<300 words, aim for 150-250 words).

**CRITICAL INSTRUCTIONS:**
1. Start with [CAMERA STATE] declaration FIRST
2. Focus on TASK/ACTION not scene description
3. Use EXACT measurements (cm, cm/s, seconds)
4. Keep it SHORT and ACTION-FOCUSED

**REQUIRED FORMAT:**

[CAMERA STATE]:
STATIC CAMERA: [exact position - "1.5m above workspace, 45-degree angle" or "top-down view, 2m height"]
CAMERA VELOCITY = 0 (fixed position)
FOV: [estimate field of view]
Background: FROZEN, no camera motion

[ACTION - SINGLE ARM TASK]:
Starting pose: Gripper at [X position with measurement, e.g., "20cm left of center, 30cm height"]
Motion sequence:
- t=0-1s: [specific action with speed, e.g., "moves right 25cm at 15 cm/s"]
- t=1-2s: [gripper action, e.g., "descends 10cm, opens to 7cm"]
- t=2-3s: [grasp/release, e.g., "closes to 5cm around object"]
- t=3-5s: [completion, e.g., "lifts 8cm, moves left 30cm to target"]
Target: [final position with measurement]

[PHYSICS]:
- Smooth acceleration: 0 → 15cm/s over 0.5s
- Gravity: object stable when gripped
- Workspace limit: [e.g., "50cm radius"]
- No instant motion, realistic joint speeds

**Generate a professional, CONCISE prompt following this exact structure. DO NOT exceed 300 words.**"""

        if additional_prompt:
            base_analysis += f"\n\nADDITIONAL TASK GUIDANCE: {additional_prompt}"

        base_analysis += "\n\nGenerate a detailed, professional prompt for 3 DOF manipulator video generation, emphasizing physical realism and manipulator constraints."

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
            raise RuntimeError(f"Failed to generate 3 DOF manipulator prompt from image: {e}")

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
        description="Generate Cosmos Predict prompts for SO-1 arm from LeRobot using Qwen2.5-VL-7B vision analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --image Inputimg/so1/pick_place.jpg
  %(prog)s --image Inputimg/so1/assembly.jpg --prompt "focus on precise placement"
  %(prog)s --image path/to/so1_arm.jpg -o so1_analysis.txt --verbose
        """
    )
    parser.add_argument("--image", "-i", type=str, required=True,
                       help="Path to image showing SO-1 arm from LeRobot")
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
        args.output = f"so1_{image_basename}_prompt.txt"

    if args.verbose:
        print("🤖 Qwen2.5-VL-7B SO-1 Arm Prompt Extender (LeRobot)")
        print(f"Image: {args.image}")
        print(f"Additional prompt: {args.prompt}")
        print(f"Output: {args.output}")
        print(f"Max tokens: {args.max_tokens}")
        print("-" * 70)

    try:
        # Initialize the SO-1 arm prompt extender
        extender = QwenSO1ArmPromptExtender(device=args.device)

        # Analyze image and generate prompt
        if args.verbose:
            print("📷 Analyzing SO-1 arm image...")
            print("🧠 Generating physics-based video prompt for arm manipulation...")

        enhanced_prompt = extender.enhance_prompt_from_image(
            args.image,
            args.prompt,
            args.max_tokens
        )

        # Display result
        print("\n🎬 Enhanced Prompt for SO-1 Arm (Cosmos Predict):")
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
                "name": f"so1_arm_{clean_name}",
                "input_path": os.path.abspath(args.image),
                "prompt": enhanced_prompt,
                "negative_prompt": "unrealistic speed, teleportation, object morphing, floating objects ignoring gravity, workspace boundary violations, collision with tabletop, gripper slipping, shaky camera, motion blur during precision tasks, poor lighting, out of focus, jerky motion, unrealistic acceleration, arm passing through objects, sudden position jumps",
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
