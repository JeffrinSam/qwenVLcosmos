#!/usr/bin/env python3
"""
Qwen2.5-VL-7B Vision-Based Prompt Extender for Cosmos Predict 2.5
SPECIALIZED FOR: BIMANUAL UR3 ROBOT SYSTEMS

This prompt extender is optimized for dual-arm Universal Robots UR3 systems,
designed for complex manipulation tasks requiring coordination between two 6 DOF arms.

UR3 Bimanual System Characteristics:
- Two UR3 collaborative robot arms (6 DOF each = 12 DOF total)
- Compact workspace optimized for tabletop manipulation
- Payload capacity: 3kg per arm
- Reach radius: 500mm per arm
- Coordinated motion: synchronized, sequential, or independent
- Common applications: assembly, dual-handed manipulation, object handoff, collaborative tasks

Example usage:
python prompt_extender_bimanual_ur3.py --image Inputimg/bimanual/assembly.jpg
python prompt_extender_bimanual_ur3.py --image Inputimg/bimanual/handoff.jpg --prompt "coordinated object transfer"

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
# Auto-detect model directory (where this script is located)
import sys
from pathlib import Path
SCRIPT_DIR = Path(__file__).parent.absolute()
MODEL_DIR = str(SCRIPT_DIR / ".." / "Qwen_instructor_7B")
DEFAULT_MAX_TOKENS = 650  # Reduced to target <300 word output (~250-280 words for complex dual-arm)

class QwenBimanualUR3PromptExtender:
    """Vision-enhanced prompt extension specialized for bimanual UR3 robot systems"""

    def __init__(self, model_path: str = MODEL_DIR, device: Optional[str] = None):
        """Initialize the bimanual UR3 prompt extender"""
        self.model_path = model_path

        # Set up device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        print(f"[BIMANUAL UR3 MODE] Using device: {self.device}")

        try:
            # Load model and processor
            print(f"Loading Qwen2.5-VL for bimanual UR3 analysis from {model_path}...")
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                device_map="auto" if self.device.type == "cuda" else None,
            ).to(self.device)

            self.processor = Qwen2_5_VLProcessor.from_pretrained(model_path)
            print("✅ Model loaded successfully for bimanual UR3 tasks!")

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}\nMake sure you've run download_qwen_instructor.py first")

        # Specialized system prompt for bimanual UR3 robotics
        # Based on official NVIDIA Cosmos 2.5 research (December 2025)
        self.system_prompt = """You are an expert robotics engineer specializing in bimanual UR3 dual-arm systems and physics-based video generation for NVIDIA Cosmos Predict 2.5.

**CRITICAL: Based on Official NVIDIA Cosmos Examples & Research:**

**MODEL UNDERSTANDING:**
- Cosmos-Reason1 VLM text encoder: specialized for physical AI and embodied reasoning
- Trained on bimanual robot demonstrations and dual-arm coordination datasets
- Understands physics intuitively: synchronized motion, handoff dynamics, collision avoidance
- Processes prompts with spatial reasoning for multi-agent coordination

**UR3 BIMANUAL EXPERTISE:**
- Universal Robots UR3: 6 DOF per arm, 500mm reach, 3kg payload
- Coordination modes: synchronized (mirror/parallel), sequential, independent, handoff
- Workspace management: overlapping workspace, collision-free path planning
- Fixed mounting: both bases stationary (table or frame-mounted)
- Gripper coordination: synchronized or independent grasp/release

**OFFICIAL PROMPT STRUCTURE (from NVIDIA Cosmos assets & research):**

**[CINEMATIC OPENING]** (Optional, 10-15 words):
- "A high-definition video showcases a bimanual robotic system..." OR
- "The scene captures two UR3 robotic arms working in coordination..." OR
- Start directly with system description if brevity needed

**[ROBOT SYSTEM & SCENE DESCRIPTION]** (35-50 words):
- Robot appearance: both arms with colors, materials, joint configurations
  * Example: "Two white UR3 robotic arms with blue joints and black cables"
  * Example: "A dual-arm system, each arm predominantly metallic gray with orange accent bands"
- Mounting: "mounted on opposite ends of a shared table" / "fixed to a common base frame"
- End-effectors: gripper types, tool attachments
  * Example: "both equipped with parallel jaw grippers"
- Setting: "industrial assembly station" / "clean laboratory workspace" / "manufacturing cell"
- Lighting: "bright overhead LED lights," "focused task lighting," "soft ambient illumination"
- Background: nearby equipment, workspace objects, environmental context

**[OBJECT & SPATIAL CONTEXT]** (20-30 words):
- Target objects with colors and materials
  * Example: "a small blue circuit board positioned centrally"
  * Example: "a cylindrical aluminum component with threaded ends"
- Object initial state and location
- Workspace surface: "textured metal table," "white workbench"
- Spatial arrangement that requires dual-arm coordination

**[COORDINATION DESCRIPTION - CORE]** (60-80 words):
**COORDINATION LANGUAGE** (critical for bimanual tasks):
- "both arms grasp simultaneously" (NVIDIA official example from kitchen_sink.txt reference)
- "working in synchronized motion" / "moving in coordinated fashion"
- "left arm secures while right arm manipulates"
- "handoff executed smoothly between grippers"
- "independent but complementary motions"

**MOTION QUALITY LANGUAGE** (from official examples):
- "smooth and coordinated" (NOT "left at 12 cm/s, right at 15 cm/s")
- "practiced synchronization" / "deliberate coordination"
- "maintains safe separation" / "collision-free trajectories"
- "steady and controlled" / "precise dual-arm manipulation"

**SENSORY DETAILS** (critical for quality):
- **Sound**: "synchronized mechanical whir," "dual motor hum," "soft clicks from both grippers"
- **Visual**: "arms cast intersecting shadows," "synchronized motion reflected in workspace"
- **Tactile**: "both grippers secure contact," "coordinated force application"

**COORDINATION SEQUENCE**:
- Initial state: both arms' positions and gripper states
- Coordination type: explicit or implied
  * Synchronized: "both arms move simultaneously toward the target"
  * Sequential: "left arm positions first, followed by right arm's approach"
  * Handoff: "left gripper releases as right gripper closes around the object"
- Motion description with key measurements when critical:
  * "positioned 40cm apart, flanking the central object"
  * "converge smoothly toward the shared target"
  * "maintain 15cm minimum separation throughout"
- Progressive coordination: emphasize "working together," "complementary actions"

**[TEMPORAL PROGRESSION]** (30-45 words):
- "As the video progresses..." (NVIDIA official pattern)
- "both arms continue their coordinated motion"
- "left arm maintains its grip while right arm transitions"
- "the handoff completes smoothly"
- Progressive state changes: "initially separated" → "converging" → "grasping simultaneously" → "completing task"

**[FINAL STATE]** (15-25 words):
- Closing description with both arms
- Final configuration: "both grippers finishing their respective tasks"
- Object final state: "held securely by both arms" / "transferred successfully"
- Scene resolution: "while the workspace remains organized"

**TOTAL WORD COUNT: 170-230 words** (flexible based on task complexity)
- Simple simultaneous grasp: 130-160 words
- Complex handoff or assembly: 200-230 words
- DON'T force 280 words unless truly complex multi-step task

**KEY PRINCIPLES (from official NVIDIA Cosmos documentation):**

1. **PHYSICAL REALISM PARAMOUNT**: Collision avoidance always maintained, realistic joint speeds, coordinated motion follows physics

2. **CINEMATIC LANGUAGE**: Use videography terms
   - "showcases," "captures," "demonstrates," "reveals"
   - "synchronized choreography" / "coordinated precision"

3. **MATERIAL & COLOR SPECIFICITY**:
   - Always specify colors: both arms, grippers, objects
   - Materials: metallic joints, rubber gripper pads, industrial finishes
   - Surface properties: matte arms, glossy objects

4. **COORDINATION EMPHASIS**: Never describe arms as independent unless task requires
   - Highlight relationship: "working together," "in coordination," "complementary"
   - Spatial awareness: "maintaining safe separation," "collision-free"
   - Synchronization cues: "simultaneously," "in tandem," "coordinated timing"

5. **ENVIRONMENTAL CONTEXT**: Never isolate system in void
   - Workspace boundaries and shared table/frame
   - Background objects and equipment
   - Lighting that captures both arms

6. **TEMPORAL CONSISTENCY LANGUAGE**:
   - "gradually," "smoothly," "transitions to"
   - "both maintain," "continue coordinating," "complete together"
   - Progressive description, NOT rigid time stamps

7. **MOTION QUALITY > NUMERICAL SPECS**:
   - ✅ "smooth synchronized motion" / "practiced coordination"
   - ✅ "safe separation maintained" / "collision-free paths"
   - ❌ "left: 12.5 cm/s, right: 15.3 cm/s"
   - Let Cosmos-Reason1 infer realistic dual-arm physics

8. **SENSORY IMMERSION**:
   - Sound: synchronized motor sounds, coordinated clicks
   - Visual: intersecting shadows, coordinated reflections
   - Tactile implied: both grippers secure, coordinated force

**CRITICAL RULES:**
✅ Use cinematic opening for complex coordination tasks
✅ Specify colors and materials for both arms and objects
✅ Include environmental context (workspace, lighting, background)
✅ Add sensory details (synchronized sounds, visual coordination cues)
✅ Progressive temporal language: "As the video progresses..."
✅ Coordination quality words: "synchronized," "coordinated," "complementary," "smooth"
✅ Collision avoidance always emphasized
✅ Describe final state with both arms for closure
✅ Flexible word count: 130-230 words based on complexity

❌ Don't over-specify with excessive numerical precision for both arms
❌ Don't ignore coordination relationship (never treat as two independent single-arm tasks)
❌ Don't skip sensory details (especially synchronized sounds)
❌ Don't allow arm collisions (always mention safe separation)
❌ Don't use vague coordination language ("work together" needs specifics)
❌ Don't force 280 words for simple simultaneous grasp tasks

**BIMANUAL-SPECIFIC TIPS:**
- ALWAYS describe spatial relationship between arms
- Emphasize "both," "simultaneous," "coordinated," "synchronized" where applicable
- Specify handoff dynamics explicitly if object transfers between arms
- Mention collision avoidance or safe separation for realism

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
        Analyze bimanual UR3 image and generate enhanced Cosmos-style prompt

        Args:
            image_path: Path to the image file showing bimanual UR3 system
            additional_prompt: Optional additional guidance text
            max_tokens: Maximum tokens for generation

        Returns:
            Enhanced prompt optimized for bimanual UR3 video generation
        """
        # Load and validate image
        image = self.load_and_validate_image(image_path)

        # Create bimanual UR3-specific analysis prompt
        base_analysis = """Analyze this bimanual UR3 image and generate a CONCISE Cosmos Predict prompt (<300 words, aim for 250-280 words).

**CRITICAL INSTRUCTIONS:**
1. Start with [CAMERA STATE] declaration FIRST
2. Focus on DUAL-ARM COORDINATION TASK not scene description
3. Use EXACT measurements (cm, cm/s, degrees/s, seconds)
4. Specify coordination mode (SYNCHRONIZED/SEQUENTIAL/HANDOFF/INDEPENDENT)

**REQUIRED FORMAT:**

[CAMERA STATE]:
STATIC CAMERA: [position - "frontal view, 2m from workspace" or "45-degree angle, elevated"]
CAMERA VELOCITY = 0 (fixed position)
FOV: Must capture both LEFT and RIGHT arms simultaneously
Background: FROZEN

[ACTION - DUAL-ARM]:
Coordination Mode: [SYNCHRONIZED / SEQUENTIAL / HANDOFF / INDEPENDENT]

LEFT ARM:
- Starting: TCP at [position with measurement, e.g., "25cm left of center, 30cm height"]
- Motion: t=[time]: [action with speed, e.g., "moves right 20cm at 12 cm/s"]
- Gripper: "opens to [X]cm at t=[time], closes to [Y]cm at t=[time]"
- Final: [position]

RIGHT ARM:
- Starting: TCP at [position]
- Motion: t=[time]: [action - specify if synchronized/sequential/independent]
- Gripper: [state transitions with timing]
- Final: [position]

Task: [brief - "handoff object" or "coordinated grasp" or "assembly"]

[PHYSICS]:
- Joint speeds: max 180°/s, smooth acceleration
- Collision avoidance: [X]cm minimum separation
- 500mm reach limit per arm
- 3kg payload max per arm
- No instant motion, coordinated dynamics
- Objects remain rigid

**Generate a professional, CONCISE dual-arm prompt following this exact structure. DO NOT exceed 300 words.**"""

        if additional_prompt:
            base_analysis += f"\n\nADDITIONAL TASK GUIDANCE: {additional_prompt}"

        base_analysis += "\n\nGenerate a detailed, professional prompt for bimanual UR3 video generation, emphasizing coordinated dual-arm manipulation with realistic physics and collision avoidance."

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
            raise RuntimeError(f"Failed to generate bimanual UR3 prompt from image: {e}")

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
        description="Generate Cosmos Predict prompts for bimanual UR3 systems using Qwen2.5-VL-7B vision analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --image Inputimg/bimanual/assembly_task.jpg
  %(prog)s --image Inputimg/bimanual/handoff.jpg --prompt "coordinated object transfer"
  %(prog)s --image path/to/dual_arm.jpg -o bimanual_analysis.txt --verbose
        """
    )
    parser.add_argument("--image", "-i", type=str, required=True,
                       help="Path to image showing bimanual UR3 system")
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
        args.output = f"bimanual_ur3_{image_basename}_prompt.txt"

    if args.verbose:
        print("🤖 Qwen2.5-VL-7B Bimanual UR3 Prompt Extender")
        print(f"Image: {args.image}")
        print(f"Additional prompt: {args.prompt}")
        print(f"Output: {args.output}")
        print(f"Max tokens: {args.max_tokens}")
        print("-" * 70)

    try:
        # Initialize the bimanual UR3 prompt extender
        extender = QwenBimanualUR3PromptExtender(device=args.device)

        # Analyze image and generate prompt
        if args.verbose:
            print("📷 Analyzing bimanual UR3 system image...")
            print("🧠 Generating physics-based dual-arm manipulation prompt...")

        enhanced_prompt = extender.enhance_prompt_from_image(
            args.image,
            args.prompt,
            args.max_tokens
        )

        # Display result
        print("\n🎬 Enhanced Prompt for Bimanual UR3 (Cosmos Predict):")
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
                "name": f"bimanual_ur3_{clean_name}",
                "input_path": os.path.abspath(args.image),
                "prompt": enhanced_prompt,
                "negative_prompt": "arm collision, unrealistic joint angles, over-extension beyond 500mm reach, payload exceeding 3kg without slow-down, instant motion without acceleration, teleportation, arms passing through each other, gripper failure, object morphing, unrealistic speed, jerky motion, joint angle violations, single arm operation when bimanual coordination needed, poor synchronization, timing errors in handoff, shaky camera, motion blur, out of focus, inconsistent lighting, missing arm visibility.",
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
