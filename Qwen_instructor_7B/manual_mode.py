#!/usr/bin/env python3
"""
Manual Mode for Cosmos Predict 2.5
MODE 1: MANUAL CONTROL (No AI Extension)

This mode gives you full manual control over all parameters.
NO AI prompt extension - you provide everything:
- Positive prompt (detailed physics-based description)
- Negative prompt (what to avoid)
- Resolution, frames, seed, guidance, etc.

Use this mode when:
- You already have a well-crafted Cosmos prompt
- You want precise control without AI modification
- You're experimenting with specific parameters

Example usage:
python manual_mode.py --image input.jpg --prompt "detailed prompt here" --negative "avoid this" --frames 77 --resolution 432x768

Prerequisites:
- None - this mode doesn't use AI models
"""

import argparse
import os
import json
import re

def main():
    parser = argparse.ArgumentParser(
        description="Manual mode for Cosmos Predict 2.5 - Full control, no AI extension",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --image robot.jpg --prompt "STATIC CAMERA at 1.5m height..." --output manual_config

  %(prog)s --image scene.jpg \\
    --prompt "STATIC CAMERA: top-down view. Robot arm moves from left to right at 10cm/s" \\
    --negative "unrealistic motion, teleportation, blurry" \\
    --frames 144 --resolution 768x432 --seed 123 --guidance 8.0

Full control example:
  %(prog)s -i input.jpg \\
    -p "STATIC CAMERA: 45-degree elevated view, 1.2m height, FOV 60 degrees. Background frozen. t=0-2s: Robot gripper descends 15cm at smooth 7.5cm/s. t=2-3s: Gripper closes from 8cm to 4cm around red cube. t=3-5s: Arm lifts 20cm upward at 10cm/s. Physics: smooth acceleration, gravity on cube." \\
    -n "jerky motion, teleportation, object morphing, unrealistic speed, motion blur" \\
    --frames 121 --resolution 432x768 --seed 42 --guidance 7.5 \\
    -o my_precise_config
        """
    )

    # Required parameters
    parser.add_argument("--image", "-i", type=str, required=True,
                       help="Path to input image")
    parser.add_argument("--prompt", "-p", type=str, required=True,
                       help="Full positive prompt (you write the complete Cosmos prompt)")

    # Optional parameters with defaults
    parser.add_argument("--negative", "-n", type=str,
                       default="unrealistic motion, teleportation, object morphing, floating objects, instant acceleration, shaky camera, motion blur, poor lighting, out of focus, jerky motion, physics violations",
                       help="Negative prompt (default: standard physics violations)")
    parser.add_argument("--output", "-o", type=str,
                       help="Output filename prefix (default: manual_<image_name>)")

    # Cosmos generation parameters
    parser.add_argument("--frames", type=int, default=77,
                       help="Number of frames (default: 77 = ~3.2s at 24fps)")
    parser.add_argument("--resolution", type=str, default="432x768",
                       help="Video resolution as WIDTHxHEIGHT (default: 432x768)")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--guidance", type=float, default=7.0,
                       help="Guidance scale (default: 7.0, higher = more prompt adherence)")
    parser.add_argument("--autoregressive", action="store_true",
                       help="Enable autoregressive mode for longer videos")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed output")

    args = parser.parse_args()

    # Validate image exists
    if not os.path.exists(args.image):
        print(f"❌ Error: Image not found: {args.image}")
        return 1

    # Parse resolution
    try:
        width, height = map(int, args.resolution.split('x'))
    except:
        print(f"❌ Error: Invalid resolution format. Use WIDTHxHEIGHT (e.g., 432x768)")
        return 1

    # Generate output filename
    if not args.output:
        image_basename = os.path.splitext(os.path.basename(args.image))[0]
        args.output = f"manual_{image_basename}"

    txt_output = f"{args.output}.txt"
    json_output = f"{args.output}.json"

    if args.verbose:
        print("=" * 70)
        print("🎯 MANUAL MODE - Full Control (No AI Extension)")
        print("=" * 70)
        print(f"Image: {args.image}")
        print(f"Positive prompt: {args.prompt[:100]}..." if len(args.prompt) > 100 else f"Positive prompt: {args.prompt}")
        print(f"Negative prompt: {args.negative[:80]}..." if len(args.negative) > 80 else f"Negative prompt: {args.negative}")
        print(f"Frames: {args.frames} (~{args.frames/24:.1f}s at 24fps)")
        print(f"Resolution: {width}x{height}")
        print(f"Seed: {args.seed}")
        print(f"Guidance: {args.guidance}")
        print(f"Autoregressive: {args.autoregressive}")
        print(f"Output: {txt_output}, {json_output}")
        print("=" * 70)

    # Save positive prompt to text file
    with open(txt_output, 'w', encoding='utf-8') as f:
        f.write(args.prompt)

    print(f"✅ Saved prompt to: {txt_output}")

    # Create Cosmos-compatible JSON
    clean_name = re.sub(r'[^\w\-_]', '_', os.path.splitext(os.path.basename(args.image))[0])[:30]

    cosmos_data = {
        "name": f"manual_{clean_name}",
        "input_path": os.path.abspath(args.image),
        "prompt": args.prompt,
        "negative_prompt": args.negative,
        "num_output_frames": args.frames,
        "resolution": f"{height},{width}",
        "seed": args.seed,
        "guidance": int(args.guidance),
        "inference_type": "image2world"
    }

    if args.autoregressive:
        cosmos_data["autoregressive"] = True

    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(cosmos_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved Cosmos-compatible JSON to: {json_output}")

    print("\n📊 Configuration Summary:")
    print(f"   Mode: Manual (no AI extension)")
    print(f"   Frames: {args.frames}")
    print(f"   Resolution: {width}x{height}")
    print(f"   Guidance: {args.guidance}")
    print(f"   Seed: {args.seed}")

    print("\n🚀 Next Steps:")
    print(f"   Run Cosmos inference:")
    print(f"   python examples/inference.py -i {json_output} -o outputs/{args.output}")

    return 0


if __name__ == "__main__":
    exit(main())
