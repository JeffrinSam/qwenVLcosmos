#!/usr/bin/env python3
"""
Batch Cosmos Pipeline - Process Multiple Images Automatically

This script allows you to process multiple images in batch mode with the same
robot type and settings, useful for generating training datasets or testing.

Example usage:
    # Process all images in a folder
    python batch_cosmos_pipeline.py --mode 2 --input-dir Inputimg/ugv --prompt "navigate forward"

    # Process specific images with a CSV file
    python batch_cosmos_pipeline.py --mode 3 --csv-file batch_tasks.csv

CSV format:
    image_path,prompt
    Inputimg/bimanual/assembly1.jpg,"both arms lift the box"
    Inputimg/bimanual/handoff.jpg,"transfer object from left to right arm"

Author: Created for Cosmos Predict 2.5
"""

import os
import sys
import json
import csv
import argparse
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Add parent directories to path
COSMOS_ROOT = Path(__file__).parent.parent
QWEN_DIR = COSMOS_ROOT / "Qwen_instructor_7B"
sys.path.insert(0, str(QWEN_DIR))


class BatchCosmosProcessor:
    """Batch processor for Cosmos video generation"""

    def __init__(self, robot_mode: str, auto_inference: bool = False):
        self.cosmos_root = COSMOS_ROOT
        self.qwen_dir = QWEN_DIR
        self.output_dir = self.cosmos_root / "reasoningcosmos" / "batch_outputs"
        self.output_dir.mkdir(exist_ok=True)

        self.robot_modes = {
            '1': {
                'name': '3 DOF Manipulator',
                'script': 'prompt_extender_3dof_manipulator.py',
            },
            '2': {
                'name': 'Mobile Robot (UGV)',
                'script': 'prompt_extender_mobile_robot.py',
            },
            '3': {
                'name': 'Bimanual UR3',
                'script': 'prompt_extender_bimanual_ur3.py',
            }
        }

        if robot_mode not in self.robot_modes:
            raise ValueError(f"Invalid robot mode: {robot_mode}")

        self.robot_mode = robot_mode
        self.auto_inference = auto_inference

    def process_image(self, image_path: Path, prompt: str,
                     settings: Dict[str, Any]) -> Tuple[bool, Optional[Path]]:
        """Process a single image"""
        robot = self.robot_modes[self.robot_mode]
        script_path = self.qwen_dir / robot['script']

        print(f"\n{'='*70}")
        print(f"Processing: {image_path.name}")
        print(f"Prompt: {prompt}")
        print(f"{'='*70}")

        # Prepare output filename
        image_stem = image_path.stem
        output_base = self.output_dir / f"batch_{self.robot_mode}_{image_stem}"
        output_txt = f"{output_base}_prompt.txt"
        output_json = f"{output_base}_prompt.json"

        # Run prompt extender
        cmd = [
            sys.executable,
            str(script_path),
            '--image', str(image_path),
            '--prompt', prompt,
            '--output', output_txt
        ]

        try:
            subprocess.run(cmd, cwd=str(self.cosmos_root), check=True,
                          capture_output=True, text=True)

            json_path = Path(output_json)
            if not json_path.exists():
                print(f"✗ JSON not created for {image_path.name}")
                return False, None

            # Update configuration
            with open(json_path, 'r') as f:
                config = json.load(f)

            config.update({
                'num_output_frames': settings.get('num_output_frames', 77),
                'seed': settings.get('seed', 42),
                'guidance': settings.get('guidance', 7),
                'resolution': settings.get('resolution', '432,768'),
                'enable_autoregressive': settings.get('enable_autoregressive', True),
                'chunk_size': settings.get('num_output_frames', 77),
                'chunk_overlap': 1,
                'input_path': str(image_path.absolute())
            })

            with open(json_path, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"✓ Generated: {json_path.name}")

            # Run inference if requested
            if self.auto_inference:
                video_output_dir = self.output_dir / json_path.stem.replace('_prompt', '_video')
                inference_script = self.cosmos_root / "examples" / "inference.py"

                cmd = [
                    sys.executable,
                    str(inference_script),
                    '-i', str(json_path),
                    '-o', str(video_output_dir),
                    '--inference-type', 'image2world'
                ]

                subprocess.run(cmd, cwd=str(self.cosmos_root), check=True)
                print(f"✓ Video generated: {video_output_dir}")

            return True, json_path

        except subprocess.CalledProcessError as e:
            print(f"✗ Error processing {image_path.name}: {e}")
            return False, None
        except Exception as e:
            print(f"✗ Unexpected error for {image_path.name}: {e}")
            return False, None

    def process_directory(self, input_dir: Path, prompt: str,
                         settings: Dict[str, Any]) -> List[Path]:
        """Process all images in a directory"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []

        for ext in image_extensions:
            image_files.extend(input_dir.glob(f'*{ext}'))
            image_files.extend(input_dir.glob(f'*{ext.upper()}'))

        if not image_files:
            print(f"No images found in {input_dir}")
            return []

        print(f"\nFound {len(image_files)} images to process")

        successful = []
        for img in image_files:
            success, json_path = self.process_image(img, prompt, settings)
            if success and json_path:
                successful.append(json_path)

        return successful

    def process_csv(self, csv_path: Path, settings: Dict[str, Any]) -> List[Path]:
        """Process images from CSV file"""
        if not csv_path.exists():
            print(f"CSV file not found: {csv_path}")
            return []

        successful = []

        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                image_path = Path(row['image_path'])
                if not image_path.is_absolute():
                    image_path = self.cosmos_root / image_path

                prompt = row['prompt']

                if image_path.exists():
                    success, json_path = self.process_image(image_path, prompt, settings)
                    if success and json_path:
                        successful.append(json_path)
                else:
                    print(f"✗ Image not found: {image_path}")

        return successful


def main():
    parser = argparse.ArgumentParser(
        description="Batch process images for Cosmos video generation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--mode', '-m', type=str, required=True, choices=['1', '2', '3'],
                       help='Robot mode: [1] 3DOF [2] Mobile [3] Bimanual')

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input-dir', '-d', type=Path,
                            help='Directory containing images')
    input_group.add_argument('--csv-file', '-c', type=Path,
                            help='CSV file with image paths and prompts')

    parser.add_argument('--prompt', '-p', type=str,
                       help='Prompt for all images (required for --input-dir)')

    parser.add_argument('--frames', type=int, default=77,
                       help='Number of output frames (default: 77)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed (default: 42)')
    parser.add_argument('--guidance', type=float, default=7,
                       help='Guidance scale (default: 7)')
    parser.add_argument('--resolution', type=str, default='432,768',
                       help='Resolution as height,width (default: 432,768)')
    parser.add_argument('--no-autoregressive', action='store_true',
                       help='Disable autoregressive mode')

    parser.add_argument('--run-inference', action='store_true',
                       help='Automatically run Cosmos inference after prompt generation')

    args = parser.parse_args()

    # Validate arguments
    if args.input_dir and not args.prompt:
        parser.error("--prompt is required when using --input-dir")

    # Prepare settings
    settings = {
        'num_output_frames': args.frames,
        'seed': args.seed,
        'guidance': args.guidance,
        'resolution': args.resolution,
        'enable_autoregressive': not args.no_autoregressive
    }

    # Create processor
    processor = BatchCosmosProcessor(args.mode, args.run_inference)

    # Process
    if args.input_dir:
        successful = processor.process_directory(args.input_dir, args.prompt, settings)
    else:
        successful = processor.process_csv(args.csv_file, settings)

    # Summary
    print(f"\n{'='*70}")
    print(f"Batch Processing Complete")
    print(f"{'='*70}")
    print(f"Successfully processed: {len(successful)} images")
    print(f"Output directory: {processor.output_dir}")
    print(f"{'='*70}\n")

    if successful and not args.run_inference:
        print("To generate videos, run:")
        print(f"python examples/inference.py -i {processor.output_dir}/*_prompt.json -o outputs/batch_videos")


if __name__ == "__main__":
    main()
