#!/usr/bin/env python3
"""
Qwen2.5-VL Vision-Based Prompt Extender for Cosmos Predict 2.5

This enhanced version analyzes single images using Qwen2.5-VL's vision capabilities,
then generates detailed, physics-aware prompts for Cosmos Predict 2.5 video generation.

Perfect for analyzing individual frames from your Inputimg/ folder and creating
video generation prompts based on visual understanding.

Example usage:
python prompt_extender2.py --image Inputimg/base/robot_welding.jpg
python prompt_extender2.py --image Inputimg/ugv/1.jpg --prompt "focus on autonomous navigation"

Prerequisites:
- Run download_qwen_instructor.py first to download the model
- Install required packages: pip install torch transformers accelerate pillow

Usage:
python prompt_extender2.py --image path/to/image.jpg [--prompt "additional guidance"]
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
MODEL_DIR = "."  # Model files are in the same directory as this script
DEFAULT_MAX_TOKENS = 700  # More tokens for vision analysis

class QwenVisionPromptExtender:
    """Vision-enhanced prompt extension using Qwen2.5-VL model"""

    def __init__(self, model_path: str = MODEL_DIR, device: Optional[str] = None):
        """
        Initialize the vision prompt extender

        Args:
            model_path: Path to the downloaded model directory
            device: Device to use ('cuda', 'cpu', or None for auto)
        """
        self.model_path = model_path

        # Set up device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        print(f"Using device: {self.device}")

        try:
            # Load model and processor
            print(f"Loading Qwen2.5-VL from {model_path}...")
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                device_map="auto" if self.device.type == "cuda" else None,
            ).to(self.device)

            self.processor = Qwen2_5_VLProcessor.from_pretrained(model_path)
            print("✅ Model loaded successfully!")

        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}\nMake sure you've run download_qwen_instructor.py first")

        # Enhanced system prompt for vision-based prompt generation
        self.system_prompt = """You are an expert video generation prompt engineer specializing in creating detailed, physics-aware prompts from single images.

Your task is to analyze the provided image and transform your visual understanding into comprehensive video generation prompts. Focus on:

VISION ANALYSIS:
- Identify all visible objects, subjects, and elements in the scene
- Analyze spatial relationships, positioning, and composition
- Detect materials, textures, lighting conditions, and colors
- Understand the context, environment, and setting
- Identify potential motion vectors and physical interactions

PHYSICS-AWARE PROMPT GENERATION:
- Create SETUP sections describing the physical scene with precision
- Define CAMERA STATE based on optimal viewing angles for the scene
- Describe realistic ACTION VECTORS that could naturally follow from the image
- Include PHYSICS CONSTRAINTS (gravity, momentum, material properties, motion laws)
- Specify VISUAL QUALITY details (lighting, motion blur, depth of field, resolution)

Generate prompts that could realistically continue the scene shown in the image into dynamic video content."""

    def load_and_validate_image(self, image_path: str) -> Image.Image:
        """Load and validate the input image"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        try:
            image = Image.open(image_path)
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return image
        except Exception as e:
            raise ValueError(f"Failed to load image: {e}")

    def enhance_prompt_from_image(self, image_path: str, additional_prompt: str = "",
                                max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
        """
        Analyze image and generate enhanced Cosmos-style prompt

        Args:
            image_path: Path to the image file
            additional_prompt: Optional additional guidance text
            max_tokens: Maximum tokens for generation

        Returns:
            Enhanced prompt with proper formatting
        """
        # Load and validate image
        image = self.load_and_validate_image(image_path)

        # Create vision analysis prompt
        base_analysis = """Analyze this image carefully and create a detailed video generation prompt. Study every element of the scene, the objects present, the environment, lighting, and potential motion dynamics.

Based on this visual analysis, generate a comprehensive prompt for video generation that includes:

PHYSICAL SETUP: Describe the scene, all visible objects, spatial relationships, environment, and physical properties observed in the image.

CAMERA STATE: Define the optimal camera positioning and settings based on the image composition.

ACTION VECTOR: Propose realistic motion and physical interactions that could naturally follow from this scene.

PHYSICS CONSTRAINTS: Include material properties, motion laws, environmental factors, and physical behaviors.

VISUAL QUALITY: Specify lighting effects, motion characteristics, visual effects, and technical details."""

        if additional_prompt:
            base_analysis += f"\n\nADDITIONAL GUIDANCE: {additional_prompt}"

        base_analysis += "\n\nGenerate a detailed, professional video generation prompt in the exact format used by physics-based video generation systems."

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

            # Process inputs (no image in inputs since it's in the text via chat template)
            model_inputs = self.processor(
                text=[text],
                images=image,  # Pass image separately for vision processing
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
            generated_ids = generated_ids[:, model_inputs['input_ids'].shape[1]:]  # Remove input
            enhanced_prompt = self.processor.decode(generated_ids[0], skip_special_tokens=True).strip()

            # Clean up and format the response
            enhanced_prompt = self._clean_and_format_response(enhanced_prompt)

            return enhanced_prompt

        except Exception as e:
            raise RuntimeError(f"Failed to generate prompt from image: {e}")


    def _clean_and_format_response(self, response: str) -> str:
        """Clean and format the model's response"""
        # Remove common artifacts
        response = response.strip()
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        if response.startswith("'") and response.endswith("'"):
            response = response[1:-1]

        # Basic formatting - ensure proper sentence structure
        response = re.sub(r'\s+', ' ', response)  # Normalize whitespace

        return response


def main():
    parser = argparse.ArgumentParser(
        description="Generate Cosmos Predict prompts from single images using Qwen2.5-VL vision analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --image Inputimg/base/robot_welding.jpg
  %(prog)s --image Inputimg/ugv/1.jpg --prompt "focus on vehicle motion" --verbose
  %(prog)s --image path/to/image.jpg -o analysis_result.txt
        """
    )
    parser.add_argument("--image", "-i", type=str, required=True,
                       help="Path to the input image file (JPG, PNG, etc.)")
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
        args.output = f"{image_basename}_enhanced_prompt.txt"

    if args.verbose:
        print("🤖 Qwen2.5-VL Vision Prompt Extender")
        print(f"Image: {args.image}")
        print(f"Additional prompt: {args.prompt}")
        print(f"Output: {args.output}")
        print(f"Max tokens: {args.max_tokens}")
        print("-" * 60)

    try:
        # Initialize the vision prompt extender
        extender = QwenVisionPromptExtender(device=args.device)

        # Analyze image and generate prompt
        if args.verbose:
            print("📷 Analyzing image...")
            print("🧠 Generating video prompt based on visual understanding...")

        enhanced_prompt = extender.enhance_prompt_from_image(
            args.image,
            args.prompt,
            args.max_tokens
        )

        # Display result
        print("\n🎬 Enhanced Prompt for Cosmos Predict:")
        print("=" * 60)
        print(enhanced_prompt)
        print("=" * 60)

        # Save to file if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(enhanced_prompt)
            print(f"\n✅ Saved enhanced prompt to: {args.output}")

        # Also save as JSON format compatible with Cosmos Predict
        if args.output:
            # Generate Cosmos-compatible JSON
            json_output = args.output.replace('.txt', '.json')

            # Extract a clean name from the image path
            image_name = os.path.splitext(os.path.basename(args.image))[0]
            clean_name = re.sub(r'[^\w\-_]', '_', image_name)[:30]

            cosmos_data = {
                "name": f"vision_{clean_name}",
                "prompt_path": args.image,  # Reference to original image
                "prompt": enhanced_prompt,
                "negative_prompt": "The video captures ugly scenes, static with no motion, motion blur, over-saturation, shaky footage, low resolution, grainy texture, pixelated images, poorly lit areas, underexposed and overexposed scenes, poor color balance, washed out colors, choppy sequences, jerky movements, low frame rate, artifacting, color banding, unnatural transitions, outdated special effects, fake elements, unconvincing visuals, poorly edited content, jump cuts, visual noise, and flickering. Overall, the video is of poor quality.",
                "seed": 42,
                "guidance": 7,
                "inference_type": "text2world"
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
