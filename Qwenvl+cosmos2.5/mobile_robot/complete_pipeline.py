#!/usr/bin/env python3
"""
Complete Qwen VL + Cosmos 2.5 Pipeline for 2-Wheel Mobile Robot
================================================================

This script provides an end-to-end pipeline that:
1. Analyzes mobile robot image with Qwen2.5-VL-7B
2. Generates enhanced Cosmos-style prompt for navigation/movement
3. Creates Cosmos Predict configuration
4. Runs video generation with Cosmos 2.5
5. Outputs final video

Usage:
    python complete_pipeline.py --image path/to/mobile_robot.jpg --prompt "navigate forward"
    python complete_pipeline.py --image path/to/ugv.jpg --prompt "turn and approach" --frames 121
"""

import argparse
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add parent directories to path
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
QWEN_DIR = PROJECT_ROOT / "Qwen_instructor_7B"
sys.path.insert(0, str(QWEN_DIR))

# Import the 2-wheel mobile robot prompt extender
from prompt_extender_2wheel_mobile import Qwen2WheelMobilePromptExtender


class MobileRobotPipeline:
    """Complete pipeline for 2-wheel mobile robot video generation"""

    def __init__(self, output_dir: str = None):
        """Initialize the pipeline"""
        self.output_dir = Path(output_dir) if output_dir else (SCRIPT_DIR.parent / "outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Qwen prompt extender
        print("=" * 60)
        print("  MOBILE ROBOT: Qwen VL + Cosmos 2.5 Pipeline")
        print("=" * 60)
        print()
        print("Step 1/4: Loading Qwen2.5-VL-7B model...")
        self.extender = Qwen2WheelMobilePromptExtender()
        print("✓ Model loaded successfully")
        print()

    def generate_video(self, image_path: str, user_prompt: str = "",
                      num_frames: int = 77, resolution: str = "432,768",
                      seed: int = 42, guidance: int = 7,
                      enable_autoregressive: bool = True,
                      chunk_size: int = 77, chunk_overlap: int = 1):
        """
        Run complete pipeline: image → Qwen analysis → Cosmos generation → video

        Args:
            image_path: Path to mobile robot image
            user_prompt: Optional user guidance for navigation/movement
            num_frames: Number of output frames (default: 77 ≈ 3.2s)
            resolution: "height,width" format
            seed: Random seed for reproducibility
            guidance: Guidance scale (0-7)
            enable_autoregressive: Enable for longer videos
            chunk_size: Frames per chunk (for autoregressive)
            chunk_overlap: Overlap between chunks

        Returns:
            Path to generated video file
        """

        # Validate inputs
        image_path = Path(image_path).absolute()
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Create timestamped output folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_name = f"mobile_robot_{timestamp}"
        job_dir = self.output_dir / job_name
        job_dir.mkdir(parents=True, exist_ok=True)

        print(f"Job: {job_name}")
        print(f"Output directory: {job_dir}")
        print()

        # Step 2: Analyze image and generate enhanced prompt
        print("Step 2/4: Analyzing image with Qwen VL...")
        print(f"  Image: {image_path.name}")
        print(f"  User guidance: {user_prompt if user_prompt else '(none - using vision only)'}")

        enhanced_prompt = self.extender.enhance_prompt_from_image(
            str(image_path),
            additional_prompt=user_prompt,
            max_tokens=600
        )

        # Save enhanced prompt
        prompt_file = job_dir / "enhanced_prompt.txt"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_prompt)

        print(f"✓ Generated enhanced prompt ({len(enhanced_prompt.split())} words)")
        print(f"  Saved to: {prompt_file.name}")
        print()

        # Display prompt preview
        print("Enhanced Prompt Preview:")
        print("-" * 60)
        preview = enhanced_prompt[:300] + "..." if len(enhanced_prompt) > 300 else enhanced_prompt
        print(preview)
        print("-" * 60)
        print()

        # Step 3: Create Cosmos Predict configuration
        print("Step 3/4: Creating Cosmos Predict configuration...")

        cosmos_config = {
            "inference_type": "image2world",
            "name": job_name,
            "input_path": str(image_path),
            "prompt": enhanced_prompt,
            "negative_prompt": "flying robot, hovering, aerial drone, floating, unstable wheels, "
                              "morphing shape, unrealistic physics, instant motion, teleportation, "
                              "blurry, shaky camera, motion blur on background, changing geometry",
            "enable_autoregressive": enable_autoregressive,
            "num_output_frames": num_frames,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "resolution": resolution,
            "seed": seed,
            "guidance": guidance
        }

        config_file = job_dir / "cosmos_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(cosmos_config, f, indent=2, ensure_ascii=False)

        print(f"✓ Configuration created:")
        print(f"  - Frames: {num_frames}")
        print(f"  - Resolution: {resolution}")
        print(f"  - Autoregressive: {enable_autoregressive}")
        print(f"  - Seed: {seed}, Guidance: {guidance}")
        print(f"  Saved to: {config_file.name}")
        print()

        # Step 4: Run Cosmos Predict inference
        print("Step 4/4: Running Cosmos Predict 2.5...")
        print("This may take several minutes depending on settings...")
        print()

        inference_script = PROJECT_ROOT / "examples" / "inference.py"

        cmd = [
            "python3",
            str(inference_script),
            "-i", str(config_file),
            "-o", str(job_dir)
        ]

        try:
            # Run inference with real-time output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=PROJECT_ROOT
            )

            # Stream output
            for line in process.stdout:
                print(f"  {line.rstrip()}")

            process.wait()

            if process.returncode != 0:
                raise RuntimeError(f"Cosmos Predict failed with return code {process.returncode}")

            print()
            print("✓ Video generation complete!")

            # Find generated video
            video_files = list(job_dir.glob("*.mp4"))
            if video_files:
                video_file = video_files[0]
                print()
                print("=" * 60)
                print("  PIPELINE COMPLETE!")
                print("=" * 60)
                print(f"Video: {video_file}")
                print(f"Prompt: {prompt_file}")
                print(f"Config: {config_file}")
                print(f"Directory: {job_dir}")
                print("=" * 60)
                return video_file
            else:
                raise FileNotFoundError("No video file was generated")

        except Exception as e:
            print(f"\n✗ Error during video generation: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Complete Qwen VL + Cosmos 2.5 pipeline for 2-wheel mobile robot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (vision only)
  %(prog)s --image path/to/mobile_robot.jpg

  # With navigation guidance
  %(prog)s --image path/to/ugv.jpg --prompt "navigate forward and turn right"

  # Longer navigation sequence
  %(prog)s --image path/to/warehouse_robot.jpg --prompt "approach target" --frames 121

  # Custom resolution and settings
  %(prog)s --image path/to/ugv.jpg --prompt "pivot and approach camera" --resolution 768,432 --seed 42
        """
    )

    parser.add_argument("--image", "-i", type=str, required=True,
                       help="Path to mobile robot image")
    parser.add_argument("--prompt", "-p", type=str, default="",
                       help="User guidance for navigation/movement (optional)")
    parser.add_argument("--frames", "-f", type=int, default=77,
                       help="Number of output frames (default: 77)")
    parser.add_argument("--resolution", "-r", type=str, default="432,768",
                       help="Resolution as 'height,width' (default: 432,768)")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed (default: 42)")
    parser.add_argument("--guidance", type=int, default=7,
                       help="Guidance scale 0-7 (default: 7)")
    parser.add_argument("--no-autoregressive", action="store_true",
                       help="Disable autoregressive mode")
    parser.add_argument("--chunk-size", type=int, default=77,
                       help="Chunk size for autoregressive (default: 77)")
    parser.add_argument("--chunk-overlap", type=int, default=1,
                       help="Chunk overlap (default: 1)")
    parser.add_argument("--output-dir", "-o", type=str,
                       help="Output directory (default: ../outputs/)")

    args = parser.parse_args()

    try:
        # Initialize pipeline
        pipeline = MobileRobotPipeline(output_dir=args.output_dir)

        # Run complete pipeline
        video_path = pipeline.generate_video(
            image_path=args.image,
            user_prompt=args.prompt,
            num_frames=args.frames,
            resolution=args.resolution,
            seed=args.seed,
            guidance=args.guidance,
            enable_autoregressive=not args.no_autoregressive,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap
        )

        print("\n✅ Success!")
        return 0

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
