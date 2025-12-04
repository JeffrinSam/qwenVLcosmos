#!/usr/bin/env python3
"""
Interactive Cosmos Pipeline - Simplified Video Generation Interface

This interactive terminal interface allows you to:
1. Choose a mode: Manual, Embodiment-Specific, or General Analyzer
2. Provide image and prompts
3. Automatically generate videos with Cosmos Predict 2.5

THREE MODES:
- Mode 1: MANUAL - Full control, you write everything (no AI extension)
- Mode 2: EMBODIMENT-SPECIFIC - AI extension tuned for SO-1, 2-wheel mobile, UR3
- Mode 3: GENERAL ANALYZER - AI analyzes any image and extends your prompt

Example:
    python interactive_cosmos_pipeline.py

Then follow the interactive prompts to select mode and configure generation.

Author: Created for Cosmos Predict 2.5
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directories to path for imports
COSMOS_ROOT = Path(__file__).parent.parent
QWEN_DIR = COSMOS_ROOT / "Qwen_instructor_7B"
sys.path.insert(0, str(QWEN_DIR))

# Color codes for terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class InteractiveCosmosInterface:
    """Interactive terminal interface for Cosmos video generation"""

    def __init__(self):
        self.cosmos_root = COSMOS_ROOT
        self.qwen_dir = QWEN_DIR
        self.output_dir = self.cosmos_root / "reasoningcosmos" / "outputs"
        self.output_dir.mkdir(exist_ok=True)

        # Mode 1: Manual control
        self.manual_mode = {
            'name': 'Manual Control',
            'script': 'manual_mode.py',
            'description': 'Full control - you provide all prompts and settings',
            'icon': '🎯'
        }

        # Mode 2: Embodiment-specific AI extension
        self.embodiment_modes = {
            '1': {
                'name': 'SO-1 Arm (LeRobot)',
                'script': 'prompt_extender_so1_arm.py',
                'description': 'Single-arm manipulation from LeRobot',
                'icon': '🦾'
            },
            '2': {
                'name': '2-Wheel Mobile Robot',
                'script': 'prompt_extender_2wheel_mobile.py',
                'description': 'Differential drive navigation',
                'icon': '🤖'
            },
            '3': {
                'name': 'Bimanual UR3',
                'script': 'prompt_extender_bimanual_ur3.py',
                'description': 'Dual-arm coordination',
                'icon': '🤝'
            }
        }

        # Mode 3: General image analyzer
        self.general_mode = {
            'name': 'General Image Analyzer',
            'script': 'prompt_extender_general.py',
            'description': 'AI analyzes any robot/scene and extends prompt',
            'icon': '🔬'
        }

    def print_header(self):
        """Print welcome header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
        print("   🎬 INTERACTIVE COSMOS PIPELINE - Robotics Video Generation")
        print(f"{'='*70}{Colors.ENDC}\n")
        print(f"{Colors.OKCYAN}Powered by: Qwen2.5-VL + Cosmos Predict 2.5{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Simple Input → Intelligent Analysis → Physics-Based Video{Colors.ENDC}\n")

    def print_mode_menu(self):
        """Print input mode selection menu"""
        print(f"{Colors.BOLD}Select Input Mode:{Colors.ENDC}\n")
        print(f"  {Colors.OKGREEN}[1]{Colors.ENDC} 📷 {Colors.BOLD}Image + Prompt{Colors.ENDC}")
        print(f"      → Analyze image with Qwen VL + extend prompt")
        print(f"      → Best for: Existing robot images\n")
        print(f"  {Colors.OKGREEN}[2]{Colors.ENDC} 📝 {Colors.BOLD}Text-Only Prompt{Colors.ENDC}")
        print(f"      → Extend prompt without image analysis")
        print(f"      → Best for: Clear text descriptions, no image available\n")

    def get_mode_selection(self) -> str:
        """Get input mode selection from user"""
        while True:
            choice = input(f"{Colors.OKCYAN}Enter mode [1-2]: {Colors.ENDC}").strip()
            if choice in ['1', '2']:
                return choice
            print(f"{Colors.FAIL}Invalid choice. Please enter 1 or 2.{Colors.ENDC}")

    def print_robot_menu(self):
        """Print robot type selection menu"""
        print(f"{Colors.BOLD}Select Robot Type:{Colors.ENDC}\n")
        for key, robot in self.robot_modes.items():
            print(f"  {Colors.OKGREEN}[{key}]{Colors.ENDC} {robot['icon']} {Colors.BOLD}{robot['name']}{Colors.ENDC}")
            print(f"      → {robot['description']}\n")

    def get_robot_selection(self) -> str:
        """Get robot type selection from user"""
        while True:
            choice = input(f"{Colors.OKCYAN}Enter choice [1-3]: {Colors.ENDC}").strip()
            if choice in self.robot_modes:
                return choice
            print(f"{Colors.FAIL}Invalid choice. Please enter 1, 2, or 3.{Colors.ENDC}")

    def get_image_path(self) -> Path:
        """Get and validate image path from user"""
        while True:
            print(f"\n{Colors.BOLD}Image Input:{Colors.ENDC}")
            path_input = input(f"{Colors.OKCYAN}Enter image path (or drag & drop): {Colors.ENDC}").strip()

            # Clean up path (remove quotes if dragged)
            path_input = path_input.strip('"').strip("'")

            image_path = Path(path_input)

            # Try relative to Cosmos root if not absolute
            if not image_path.is_absolute():
                image_path = self.cosmos_root / path_input

            if image_path.exists() and image_path.is_file():
                # Check if it's an image file
                if image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                    print(f"{Colors.OKGREEN}✓ Image found: {image_path}{Colors.ENDC}")
                    return image_path
                else:
                    print(f"{Colors.WARNING}Warning: File may not be an image. Continue anyway? [y/n]{Colors.ENDC}")
                    if input().strip().lower() == 'y':
                        return image_path
            else:
                print(f"{Colors.FAIL}✗ Image not found: {image_path}{Colors.ENDC}")
                print(f"{Colors.WARNING}Please provide a valid image path.{Colors.ENDC}")

    def get_user_prompt(self) -> str:
        """Get simple natural language prompt from user"""
        print(f"\n{Colors.BOLD}Task Description:{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Enter a simple, natural language description of what the robot should do.{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Examples:{Colors.ENDC}")
        print(f"  • 'pick up the apple using right hand'")
        print(f"  • 'navigate forward and turn left to avoid obstacle'")
        print(f"  • 'both arms lift the box together'\n")

        prompt = input(f"{Colors.OKCYAN}Your prompt: {Colors.ENDC}").strip()

        while not prompt:
            print(f"{Colors.WARNING}Prompt cannot be empty.{Colors.ENDC}")
            prompt = input(f"{Colors.OKCYAN}Your prompt: {Colors.ENDC}").strip()

        print(f"{Colors.OKGREEN}✓ Prompt received{Colors.ENDC}")
        return prompt

    def get_advanced_settings(self) -> Dict[str, Any]:
        """Get optional advanced settings"""
        print(f"\n{Colors.BOLD}Advanced Settings (Optional):{Colors.ENDC}")
        use_advanced = input(f"{Colors.OKCYAN}Configure advanced settings? [y/N]: {Colors.ENDC}").strip().lower()

        settings = {
            'num_output_frames': 77,
            'seed': 42,
            'guidance': 7,
            'resolution': '432,768',
            'enable_autoregressive': True,
        }

        if use_advanced == 'y':
            print(f"\n{Colors.OKBLUE}Press Enter to use default values in [brackets]{Colors.ENDC}\n")

            # Number of frames
            frames = input(f"Number of output frames [{settings['num_output_frames']}]: ").strip()
            if frames:
                try:
                    settings['num_output_frames'] = int(frames)
                except ValueError:
                    print(f"{Colors.WARNING}Invalid input, using default{Colors.ENDC}")

            # Seed
            seed = input(f"Random seed [{settings['seed']}]: ").strip()
            if seed:
                try:
                    settings['seed'] = int(seed)
                except ValueError:
                    print(f"{Colors.WARNING}Invalid input, using default{Colors.ENDC}")

            # Guidance
            guidance = input(f"Guidance scale [{settings['guidance']}]: ").strip()
            if guidance:
                try:
                    settings['guidance'] = float(guidance)
                except ValueError:
                    print(f"{Colors.WARNING}Invalid input, using default{Colors.ENDC}")

            # Resolution
            resolution = input(f"Resolution (height,width) [{settings['resolution']}]: ").strip()
            if resolution:
                settings['resolution'] = resolution

            # Autoregressive
            autoreg = input(f"Enable autoregressive mode? [Y/n]: ").strip().lower()
            if autoreg == 'n':
                settings['enable_autoregressive'] = False

        return settings

    def run_prompt_extender(self, robot_choice: str, mode: str, image_path: Optional[Path],
                           user_prompt: str) -> Optional[Path]:
        """Run the selected prompt extender"""
        robot = self.robot_modes[robot_choice]

        # Select appropriate script based on mode
        if mode == '1':  # Image + Prompt
            script_path = self.qwen_dir / robot['script_image']
            analysis_msg = "🧠 Analyzing image with Qwen2.5-VL..."
        else:  # Text-only
            script_path = self.qwen_dir / robot['script_text']
            analysis_msg = "🧠 Extending prompt with Qwen2.5-VL..."

        print(f"\n{Colors.BOLD}Running {robot['name']} Analysis...{Colors.ENDC}")
        print(f"{Colors.OKBLUE}{analysis_msg}{Colors.ENDC}")

        # Prepare output filename
        if mode == '1' and image_path:
            image_stem = image_path.stem
            output_base = self.output_dir / f"cosmos_{robot_choice}_{image_stem}"
        else:
            # For text-only, use prompt-based filename
            clean_prompt = user_prompt[:20].replace(' ', '_')
            output_base = self.output_dir / f"cosmos_{robot_choice}_text_{clean_prompt}"

        output_txt = f"{output_base}_prompt.txt"
        output_json = f"{output_base}_prompt.json"

        # Build command based on mode
        if mode == '1':  # Image + Prompt
            cmd = [
                sys.executable,
                str(script_path),
                '--image', str(image_path),
                '--prompt', user_prompt,
                '--output', output_txt,
                '--verbose'
            ]
        else:  # Text-only
            cmd = [
                sys.executable,
                str(script_path),
                '--prompt', user_prompt,
                '--output', output_txt,
                '--verbose'
            ]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.cosmos_root),
                capture_output=False,
                text=True,
                check=True
            )

            # Check if JSON was created
            json_path = Path(output_json)
            if json_path.exists():
                print(f"{Colors.OKGREEN}✓ Prompt generation complete!{Colors.ENDC}")
                print(f"{Colors.OKGREEN}  📄 Text prompt: {output_txt}{Colors.ENDC}")
                print(f"{Colors.OKGREEN}  📋 JSON config: {output_json}{Colors.ENDC}")
                return json_path
            else:
                print(f"{Colors.FAIL}✗ JSON file not created{Colors.ENDC}")
                return None

        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}✗ Error running prompt extender: {e}{Colors.ENDC}")
            return None
        except FileNotFoundError:
            print(f"{Colors.FAIL}✗ Prompt extender script not found: {script_path}{Colors.ENDC}")
            print(f"{Colors.WARNING}Make sure Qwen model is downloaded (run download_qwen_instructor.py){Colors.ENDC}")
            return None

    def update_json_config(self, json_path: Path, settings: Dict[str, Any],
                          image_path: Optional[Path]) -> bool:
        """Update JSON configuration with advanced settings"""
        try:
            with open(json_path, 'r') as f:
                config = json.load(f)

            # Update settings
            config['num_output_frames'] = settings['num_output_frames']
            config['seed'] = settings['seed']
            config['guidance'] = settings['guidance']
            config['resolution'] = settings['resolution']
            config['enable_autoregressive'] = settings['enable_autoregressive']
            config['chunk_size'] = settings['num_output_frames']
            config['chunk_overlap'] = 1

            # Set input_path only if image provided (for image2world)
            if image_path:
                config['input_path'] = str(image_path.absolute())
                # Ensure inference_type is image2world
                if 'inference_type' not in config or config['inference_type'] == 'text2world':
                    config['inference_type'] = 'image2world'

            # Save updated config
            with open(json_path, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"{Colors.OKGREEN}✓ Configuration updated{Colors.ENDC}")
            return True

        except Exception as e:
            print(f"{Colors.FAIL}✗ Error updating configuration: {e}{Colors.ENDC}")
            return False

    def display_config_summary(self, json_path: Path):
        """Display summary of configuration"""
        try:
            with open(json_path, 'r') as f:
                config = json.load(f)

            print(f"\n{Colors.BOLD}{'='*70}")
            print("Configuration Summary")
            print(f"{'='*70}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}Name:{Colors.ENDC} {config.get('name', 'N/A')}")
            print(f"{Colors.OKBLUE}Type:{Colors.ENDC} {config.get('inference_type', 'N/A')}")
            print(f"{Colors.OKBLUE}Frames:{Colors.ENDC} {config.get('num_output_frames', 'N/A')}")
            print(f"{Colors.OKBLUE}Resolution:{Colors.ENDC} {config.get('resolution', 'N/A')}")
            print(f"{Colors.OKBLUE}Guidance:{Colors.ENDC} {config.get('guidance', 'N/A')}")
            print(f"{Colors.OKBLUE}Seed:{Colors.ENDC} {config.get('seed', 'N/A')}")
            print(f"{Colors.OKBLUE}Autoregressive:{Colors.ENDC} {config.get('enable_autoregressive', False)}")
            print(f"\n{Colors.BOLD}Enhanced Prompt Preview:{Colors.ENDC}")
            prompt = config.get('prompt', '')
            if len(prompt) > 200:
                print(f"{Colors.OKCYAN}{prompt[:200]}...{Colors.ENDC}")
            else:
                print(f"{Colors.OKCYAN}{prompt}{Colors.ENDC}")
            print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

        except Exception as e:
            print(f"{Colors.WARNING}Could not display config summary: {e}{Colors.ENDC}")

    def run_cosmos_inference(self, json_path: Path) -> bool:
        """Run Cosmos inference to generate video"""
        print(f"\n{Colors.BOLD}Running Cosmos Inference...{Colors.ENDC}")
        print(f"{Colors.OKBLUE}🎬 Generating video (this may take several minutes)...{Colors.ENDC}")

        # Prepare output directory
        video_output_dir = self.output_dir / json_path.stem.replace('_prompt', '_video')

        # Run inference
        inference_script = self.cosmos_root / "examples" / "inference.py"

        # Don't pass --inference-type on command line, it's in the JSON
        cmd = [
            sys.executable,
            str(inference_script),
            '-i', str(json_path),
            '-o', str(video_output_dir)
        ]

        print(f"{Colors.OKCYAN}Command: {' '.join(cmd)}{Colors.ENDC}\n")

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.cosmos_root),
                check=True
            )

            print(f"\n{Colors.OKGREEN}✓ Video generation complete!{Colors.ENDC}")
            print(f"{Colors.OKGREEN}📁 Output directory: {video_output_dir}{Colors.ENDC}")

            # List generated files
            if video_output_dir.exists():
                video_files = list(video_output_dir.glob('*.mp4'))
                if video_files:
                    print(f"{Colors.OKGREEN}🎥 Generated videos:{Colors.ENDC}")
                    for vf in video_files:
                        print(f"   {vf}")

            return True

        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}✗ Error running Cosmos inference: {e}{Colors.ENDC}")
            print(f"{Colors.WARNING}Check that Cosmos models are properly installed.{Colors.ENDC}")
            return False
        except FileNotFoundError:
            print(f"{Colors.FAIL}✗ Inference script not found: {inference_script}{Colors.ENDC}")
            return False

    def run(self):
        """Main interactive loop"""
        self.print_header()

        try:
            # Step 1: Select input mode (Image+Prompt or Text-only)
            self.print_mode_menu()
            mode = self.get_mode_selection()
            mode_name = "📷 Image + Prompt" if mode == '1' else "📝 Text-Only Prompt"
            print(f"\n{Colors.OKGREEN}✓ Mode: {mode_name}{Colors.ENDC}")

            # Step 2: Select robot type
            self.print_robot_menu()
            robot_choice = self.get_robot_selection()
            print(f"\n{Colors.OKGREEN}✓ Selected: {self.robot_modes[robot_choice]['icon']} {self.robot_modes[robot_choice]['name']}{Colors.ENDC}")

            # Step 3: Get image path (only for Image+Prompt mode)
            image_path = None
            if mode == '1':
                image_path = self.get_image_path()
            else:
                print(f"\n{Colors.OKBLUE}ℹ Text-only mode: No image required{Colors.ENDC}")

            # Step 4: Get user prompt
            user_prompt = self.get_user_prompt()

            # Step 5: Get advanced settings
            settings = self.get_advanced_settings()

            # Step 6: Run prompt extender
            print(f"\n{Colors.BOLD}{'='*70}")
            print("Processing...")
            print(f"{'='*70}{Colors.ENDC}")

            json_path = self.run_prompt_extender(robot_choice, mode, image_path, user_prompt)

            if not json_path:
                print(f"\n{Colors.FAIL}✗ Failed to generate prompt. Exiting.{Colors.ENDC}")
                return 1

            # Step 7: Update configuration
            self.update_json_config(json_path, settings, image_path)

            # Step 8: Display summary
            self.display_config_summary(json_path)

            # Step 9: Ask to run inference
            run_inference = input(f"{Colors.BOLD}Generate video now? [Y/n]: {Colors.ENDC}").strip().lower()

            if run_inference != 'n':
                success = self.run_cosmos_inference(json_path)

                if success:
                    print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 SUCCESS! Video generated successfully!{Colors.ENDC}")
                else:
                    print(f"\n{Colors.WARNING}Video generation failed, but config is saved at:{Colors.ENDC}")
                    print(f"{Colors.OKCYAN}{json_path}{Colors.ENDC}")
                    print(f"\n{Colors.OKBLUE}You can run it manually later with:{Colors.ENDC}")
                    print(f"{Colors.OKCYAN}python examples/inference.py -i {json_path} -o outputs/my_video{Colors.ENDC}")
            else:
                print(f"\n{Colors.OKBLUE}Configuration saved. Run inference later with:{Colors.ENDC}")
                print(f"{Colors.OKCYAN}python examples/inference.py -i {json_path} -o outputs/my_video{Colors.ENDC}")

            print(f"\n{Colors.OKGREEN}{'='*70}")
            print("Pipeline Complete!")
            print(f"{'='*70}{Colors.ENDC}\n")

            return 0

        except KeyboardInterrupt:
            print(f"\n\n{Colors.WARNING}Interrupted by user. Exiting...{Colors.ENDC}")
            return 1
        except Exception as e:
            print(f"\n{Colors.FAIL}✗ Unexpected error: {e}{Colors.ENDC}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    """Entry point"""
    interface = InteractiveCosmosInterface()
    return interface.run()


if __name__ == "__main__":
    sys.exit(main())
