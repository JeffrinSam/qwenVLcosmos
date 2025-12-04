#!/usr/bin/env python3
"""Update interactive_cosmos_pipeline.py for new 3-mode system"""

import re

with open('interactive_cosmos_pipeline.py', 'r') as f:
    content = f.read()

# Update header description
old_header = """This interactive terminal interface allows you to:
1. Choose a robot type (3 DOF manipulator, mobile robot, or bimanual UR3)
2. Provide a simple image and natural language prompt
3. Automatically generate detailed Cosmos-compatible prompts using Qwen VL
4. Optionally run Cosmos inference directly to generate videos

Example:
    python interactive_cosmos_pipeline.py

Then follow the interactive prompts:
    - Select robot type: [1] 3 DOF  [2] Mobile Robot  [3] Bimanual UR3
    - Provide image path: Inputimg/ugv/4.jpg
    - Enter simple prompt: "navigate forward and turn left to avoid obstacle"
    - Generate video? [y/n]"""

new_header = """This interactive terminal interface allows you to:
1. Choose a mode: Manual, Embodiment-Specific, or General Analyzer
2. Provide image and prompts
3. Automatically generate videos with Cosmos Predict 2.5

THREE MODES:
- Mode 1: MANUAL - Full control, you write everything (no AI extension)
- Mode 2: EMBODIMENT-SPECIFIC - AI extension tuned for SO-1, 2-wheel mobile, UR3
- Mode 3: GENERAL ANALYZER - AI analyzes any image and extends your prompt

Example:
    python interactive_cosmos_pipeline.py

Then follow the interactive prompts to select mode and configure generation."""

content = content.replace(old_header, new_header)

# Update robot_modes dictionary
old_robot_modes = """        self.robot_modes = {
            '1': {
                'name': '3 DOF Manipulator',
                'script_image': 'prompt_extender_3dof_manipulator.py',
                'script_text': 'prompt_extender_3dof_manipulator_text.py',
                'description': 'SCARA, delta, cartesian robots for pick-and-place',
                'icon': '🦾'
            },
            '2': {
                'name': 'Mobile Robot (UGV)',
                'script_image': 'prompt_extender_mobile_robot.py',
                'script_text': 'prompt_extender_mobile_robot_text.py',
                'description': 'Wheeled/tracked robots for navigation',
                'icon': '🤖'
            },
            '3': {
                'name': 'Bimanual UR3',
                'script_image': 'prompt_extender_bimanual_ur3.py',
                'script_text': 'prompt_extender_bimanual_ur3_text.py',
                'description': 'Dual-arm coordination and manipulation',
                'icon': '🦿'
            }
        }"""

new_robot_modes = """        # Mode 1: Manual control
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
        }"""

content = content.replace(old_robot_modes, new_robot_modes)

# Write updated content
with open('interactive_cosmos_pipeline.py', 'w') as f:
    f.write(content)

print("✓ Updated robot_modes to 3-mode system")
print("Note: Menu functions still need manual updates")
