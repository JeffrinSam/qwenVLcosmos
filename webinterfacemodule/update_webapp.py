#!/usr/bin/env python3
"""Update web app for 3-mode system"""

with open('app.py', 'r') as f:
    content = f.read()

# Update ROBOT_MODES configuration
old_robot_modes = """# Robot configurations
ROBOT_MODES = {
    '3dof': {
        'name': '3 DOF Manipulator',
        'script_image': 'prompt_extender_3dof_manipulator.py',
        'script_text': 'prompt_extender_3dof_manipulator_text.py',
        'description': 'SCARA, delta, cartesian robots for pick-and-place',
        'icon': '🦾'
    },"""

new_robot_modes = """# Mode configurations
# Mode 1: Manual (no scripts needed, direct config creation)
# Mode 2: Embodiment-specific
EMBODIMENT_MODES = {
    'so1': {
        'name': 'SO-1 Arm (LeRobot)',
        'script': 'prompt_extender_so1_arm.py',
        'description': 'Single-arm manipulation from LeRobot',
        'icon': '🦾'
    },
    '2wheel': {
        'name': '2-Wheel Mobile Robot',
        'script': 'prompt_extender_2wheel_mobile.py',
        'description': 'Differential drive navigation',
        'icon': '🤖'
    },
    'bimanual': {
        'name': 'Bimanual UR3',
        'script': 'prompt_extender_bimanual_ur3.py',
        'description': 'Dual-arm coordination',
        'icon': '🤝'
    }
}

# Mode 3: General analyzer
GENERAL_MODE = {
    'name': 'General Image Analyzer',
    'script': 'prompt_extender_general.py',
    'description': 'AI analyzes any robot/scene',
    'icon': '🔬'
}

# Legacy support - map old to new
ROBOT_MODES = {
    '3dof': {
        'name': '3 DOF Manipulator',
        'script_image': 'prompt_extender_3dof_manipulator.py',
        'script_text': 'prompt_extender_3dof_manipulator_text.py',
        'description': 'SCARA, delta, cartesian robots for pick-and-place',
        'icon': '🦾'
    },"""

content = content.replace(old_robot_modes, new_robot_modes)

# Update the rest of ROBOT_MODES
content = content.replace(
    "'ugv': {",
    "'ugv': {  # Legacy"
)

# Write updated content
with open('app.py', 'w') as f:
    f.write(content)

print("✓ Updated web app with new mode structure")
print("Note: Route handlers and templates still need manual updates")
