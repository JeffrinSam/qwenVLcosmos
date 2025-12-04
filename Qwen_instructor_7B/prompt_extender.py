#!/usr/bin/env python3
"""
Qwen2.5-VL Prompt Extender for Cosmos Predict 2.5

This script uses the Qwen2.5-VL-3B-Instruct model to enhance basic prompts into
detailed, physics-aware descriptions suitable for Cosmos Predict 2.5 video generation.

Example usage:
python prompt_extender.py --prompt "robot moving"
Output: Detailed prompt with SETUP, CAMERA STATE, ACTION VECTOR, etc.

Prerequisites:
- Run download_qwen_instructor.py first to download the model
- Install required packages: pip install torch transformers accelerate

Usage:
python prompt_extender.py --prompt "basic prompt here" [-o output_file] [--verbose]
"""

import argparse
import os
import torch
from transformers import Qwen2_5_VLForConditionalGeneration, Qwen2_5_VLProcessor
import json
from typing import Optional

# Configuration
MODEL_DIR = "."  # Model files are in the same directory as this script
DEFAULT_MAX_TOKENS = 512

class QwenPromptExtender:
    """Prompt enhancement class using Qwen2.5-VL model"""

    def __init__(self, model_path: str = MODEL_DIR, device: Optional[str] = None):
        """
        Initialize the prompt extender

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

        self.system_prompt = """You are an expert prompt engineer for video generation models. Your task is to take simple, basic prompts and transform them into detailed, comprehensive descriptions that will generate high-quality physics-based videos.

For video generation prompts, you should include:

1. PHYSICAL SETUP: Describe the scene, objects, and environment with precise physical details
2. CAMERA STATE: Define camera position, movement, and basic settings
3. ACTION VECTOR: Describe the motion, timing, and physical interactions
4. PHYSICS CONSTRAINTS: Include realistic physical laws, motion constraints, and natural behaviors
5. VISUAL QUALITY: Specify lighting, materials, motion blur, and technical details

Transform simple prompts like "robot moving" into detailed descriptions with proper formatting."""


    def enhance_prompt(self, basic_prompt: str, max_tokens: int = DEFAULT_MAX_TOKENS) -> str:
        """
        Enhance a basic prompt into a detailed Cosmos-style prompt

        Args:
            basic_prompt: Simple input prompt (e.g., "robot moving")
            max_tokens: Maximum tokens for generation

        Returns:
            Enhanced prompt with proper formatting
        """

        # Create enhancement prompt
        enhancement_query = f"""Take this simple prompt and enhance it into a detailed, physics-aware description for video generation:

Simple prompt: "{basic_prompt}"

Please create a detailed video generation prompt that includes:
- Clear SETUP section with scene description
- CAMERA STATE with position and movement details
- ACTION VECTOR with precise motion description
- PHYSICS constraints and realistic behaviors
- Professional formatting and terminology

Enhanced prompt:"""

        try:
            # Process the text input
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": enhancement_query}
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

            # Clean up the response
            enhanced_prompt = self._clean_response(enhanced_prompt)

            return enhanced_prompt

        except Exception as e:
            raise RuntimeError(f"Failed to enhance prompt: {e}")


    def _clean_response(self, response: str) -> str:
        """Clean and format the model's response"""
        # Remove common artifacts
        response = response.strip()
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        if response.startswith("'") and response.endswith("'"):
            response = response[1:-1]

        return response


def main():
    parser = argparse.ArgumentParser(description="Enhance basic prompts using Qwen2.5-VL for Cosmos Predict")
    parser.add_argument("--prompt", type=str, required=True, help="Basic prompt to enhance")
    parser.add_argument("--output", "-o", type=str, help="Output file to save enhanced prompt (optional)")
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS, help="Maximum tokens for generation")
    parser.add_argument("--device", type=str, choices=['cpu', 'cuda'], help="Device to use (default: auto)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        print(f"Input prompt: {args.prompt}")
        print(f"Output file: {args.output}")
        print(f"Max tokens: {args.max_tokens}")
        print("-" * 50)

    try:
        # Initialize the prompt extender
        extender = QwenPromptExtender(device=args.device)

        # Enhance the prompt
        if args.verbose:
            print("Enhancing prompt...")

        enhanced_prompt = extender.enhance_prompt(args.prompt, args.max_tokens)

        # Display result
        print("Enhanced Prompt:")
        print("=" * 50)
        print(enhanced_prompt)
        print("=" * 50)

        # Save to file if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(enhanced_prompt)
            print(f"✅ Saved enhanced prompt to: {args.output}")

        # Also save as JSON format compatible with Cosmos Predict
        if args.output:
            json_output = args.output.replace('.txt', '.json')
            cosmos_data = {
                "name": f"enhanced_{args.prompt.replace(' ', '_')[:20]}",
                "prompt_path": None,
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
